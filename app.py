from shiny import App, ui, render, reactive
from ehtools.diatipico import *
from ehtools.plot import *
from pathlib import Path
from ehtools.funciones import *
from ehtools.diccionaries import *
from shinywidgets import output_widget, render_plotly
import asyncio
from io import StringIO
from datetime import date

timezone = pytz.timezone('America/Mexico_City')
app_dir = Path(__file__).parent

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
                            {"1": "Capa homogénea"},  
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
            ui.nav_panel("Temperaturas", output_widget("grafica_Temperatura")),
            ui.nav_panel("Radiación", output_widget("grafica_Radiacion")),
            ui.nav_panel("Resultados", ui.output_text("resultados")),
            ui.nav_panel("Datos", ui.output_data_frame("get_day_data"),
            ui.download_button("downloadData", "Download")),
            ui.nav_panel("Documentación", ui.output_text("documentacion")),
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
    def grafica_Temperatura():
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
        
        fig = plot_T(dia)
        return fig

    @output
    @render_plotly
    def grafica_Radiacion():
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
        
        fig = plot_I(dia)
        return fig

    @output
    @render.text
    def resultados():
        lugar = input.place()
        mes = input.periodo()
        ubicacion = input.ubicacion()
        orienta = input.orientacion()
        abs = input.abstrac()
        sistemas = input.sistemas()
        condicion = input.Conditional()
        tipo = input.type()
        e1 = input.espesor1()
        m1 = input.material1()
        e2 = input.espesor2()
        m2 = input.material2()
        e3 = input.espesor3()
        m3 = input.material3()
        e4 = input.espesor4()
        m4 = input.material4()
        e5 = input.espesor5()
        m5 = input.material5()
        
        espesores = []
        materiales = []
        
        for i in range(1, sistemas + 1):
            espesor = locals()[f"e{i}"]
            material = locals()[f"m{i}"]
            espesores.append(espesor)
            materiales.append(material)

        resultado = f"Lugar: {lugar}, Mes: {mes}, Ubicacion: {ubicacion}, Orientacion: {orienta}, Absortancia: {abs}, Sistemas: {sistemas}, Condicion: {condicion}, Tipo de sistema: {tipo}"

        for i in range(sistemas):
            resultado += f", Espesor {i+1}: {espesores[i]}, Material {i+1}: {materiales[i]}"

        return resultado
        
    @output
    @render.data_frame
    def get_day_data():
            place = input.place()
            ruta_epw = ruta(place)  
            mes = meses_dict[input.periodo()]  
            caracteristicas = cargar_caracteristicas(place)  
            absortancia = input.absortance_value() 
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

    @render.download(
        filename=lambda: f"datos-{date.today().isoformat()}.csv"
    )
    async def downloadData():
            place = input.place()
            ruta_epw = ruta(place)  
            mes = meses_dict[input.periodo()]  
            caracteristicas = cargar_caracteristicas(place)  
            absortancia = input.absortance_value() 
            surface_tilt = location[input.ubicacion()] 
            surface_azimuth = orientacion[input.orientacion()]  

            data = calculate_day(
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
            
            data_= data[::3600]
            csv_buffer = StringIO()
            data_.to_csv(csv_buffer,index=True)
            csv_buffer.seek(0)

            await asyncio.sleep(0.25)
            yield csv_buffer.read()



app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
