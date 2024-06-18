from shiny import App, ui, render, reactive
from ehtools.diatipico import *
from ehtools.plot import *
from pathlib import Path
from ehtools.funciones import *
import pandas as pd
from pvlib import irradiance, location
from shinywidgets import output_widget, render_plotly
import random
from datetime import date

timezone = pytz.timezone('America/Mexico_City')
app_dir = Path(__file__).parent
    
meses_dict = {
    "Enero": "01",
    "Febrero": "02",
    "Marzo": "03",
    "Abril": "04",
    "Mayo": "05",
    "Junio": "06",
    "Julio": "07",
    "Agosto": "08",
    "Septiembre": "09",
    "Octubre": "10",
    "Noviembre": "11",
    "Diciembre": "12",
}

location={
    "Muro": 90,
    "Techo": 0,
}

orientacion = {
    "Norte": 0,
    "Noreste": 45,
    "Este": 90, 
    "Sureste": 135, 
    "Sur": 180,
    "Suroeste": 225, 
    "Oeste": 270, 
    "Noroeste": 315,
}

Absorbance = {
    "Aluminio pulido": 0.10,
    "Aluminio oxidado": 0.15,
    "Impermeabilizante o pintura blanca nueva": 0.15,
    "Impermeabilizante o pintura blanca": 0.20,
    "Pintura aluminio": 0.2,
    "Lámina galvanizada brillante": 0.25,
    "Pintura colores claros": 0.3,
    "Recubrimiento elastomérico blanco": 0.30,
    "Acero" : 0.45,
    "Pintura colores intermedios": 0.50,
    "Concreto claro o adocreto claro": 0.60,
    "Ladrillo rojo": 0.65,
    "Impermeabilizante rojo terracota": 0.70,
    "Lámina galvanizada": 0.7,
    "Pintura colores oscuros": 0.7,
    "Teja roja": 0.7,
    "Concreto": 0.7,
    "Impermeabilizante o pintura negra": 0.90,
    "Asfalto nuevo": 0.95,
    "Impermeabilizante o pintura negra mate nueva": 0.95,
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.accordion(
            ui.accordion_panel(
                "Cambios",
                ui.output_ui("left_controls"),
            ),
        ),
        
        ui.accordion(
            ui.accordion_panel(
                "Selección",
                    ui.output_ui("controls_top"),
                        ui.input_select(  
                            "type",  
                            "Tipo de sistema:",  
                            {"1": "Capa homogénea", "2": "Modelo 2D"},  
                        ),
            ),
        ),

        ui.accordion(
            ui.accordion_panel(
                "Datos",
                ui.output_ui("controls_rigth")
            ),
        ),
    ),
        ui.navset_card_underline(
            ui.nav_panel("Gráfica", output_widget("grafica_mes")),
            ui.nav_panel("Resultados", ui.output_text("pendiente")),
            ui.nav_panel("Datos", ui.output_data_frame("get_day_data"),
            ui.download_button("downloadData", "Download")),
            title="Datos Gráficados",
        ),
    
    ui.include_css(app_dir / "styles.css"),
    title="Ener-Habitat Phy",
    fillable=True,
)

def server(input, output, session):
    @output
    @render.ui
    def left_controls():
        type = input.type()
        return controls_left(type, 
                    lugares, 
                    meses_dict, 
                    location, 
                    orientacion, 
                    Absorbance)
    
    @output
    @render.ui
    def absortance():
        selected = input.abstrac()
        value = Absorbance.get(selected, 0.10)
        return absortance_value(value)
    
    @output
    @render.ui
    def controls_top():
        type = input.type()
        return top_controls(type)
    
    @output
    @render.ui
    def controls_rigth():
        type = input.type()
        return rigth_controls(type, materiales)
    
    @output
    @render.ui
    def campos():
        num = input.sistemas()
        return info_right(num, materiales)

    @output
    @render_plotly
    def grafica_mes():
        place = input.place()
        ruta_epw = ruta(place)
        mes = meses_dict[input.periodo()]
        caracteristicas = cargar_caracteristicas(place)
        absortancia = input.absortance_value() #0.3
        surface_tilt = location[input.ubicacion()]  # ubicacion
        surface_azimuth = orientacion[input.orientacion()] #270

        dia = calculate_day(
            ruta_epw,
            caracteristicas['lat'],
            caracteristicas['lon'],
            caracteristicas['alt'],
            mes,
            absortancia,
            surface_tilt,
            surface_azimuth,
            timezone
        )
        
        fig = plot_T_I(dia)
        return fig

    @output
    @render.text
    def pendiente():
        lugar = input.place()
        mes = input.periodo()
        ubicacion = input.ubicacion()
        orienta = input.orientacion()
        abs = input.abstrac()
        sistemas = input.sistemas()
        condicion = input.Conditional()
        tipo = input.type()
        return f"Lugar: {lugar}, Mes: {mes}, Ubicacion: {ubicacion}, Orientacion: {orienta}, Absortancia: {abs}, Sistemas: {sistemas}, Condicion: {condicion}, Tipo: {tipo}"

    @output
    @render.data_frame
    def get_day_data():
            place = input.place()
            ruta_epw = ruta(place)  
            mes = meses_dict[input.periodo()]  
            caracteristicas = cargar_caracteristicas(place)  
            absortancia = Absorbance[input.abstrac()]  
            surface_tilt = location[input.ubicacion()] 
            surface_azimuth = orientacion[input.orientacion()]  

            result = calculate_day(
                ruta_epw,
                caracteristicas['lat'],
                caracteristicas['lon'],
                caracteristicas['alt'],
                mes,
                absortancia,
                surface_tilt,
                surface_azimuth,
                timezone
            )
            
            return result[::3600] 

    @render.download(filename="data.csv")
    def downloadData():
        place = input.place()
        ruta_epw = ruta(place)  
        mes = meses_dict[input.periodo()]  
        caracteristicas = cargar_caracteristicas(place)  
        absortancia = Absorbance[input.abstrac()]  
        surface_tilt = location[input.ubicacion()] 
        surface_azimuth = orientacion[input.orientacion()]  

        df = calculate_day(
            ruta_epw,
            caracteristicas['lat'],
            caracteristicas['lon'],
            caracteristicas['alt'],
            mes,
            absortancia,
            surface_tilt,
            surface_azimuth,
            timezone
        )
        
        print(df)
        
        return df[::3600] 



app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
