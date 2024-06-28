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
from info.modal_run import info_modal

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
            ui.nav_panel("Temperaturas", output_widget("temperatura")),
            ui.nav_panel("Radiación", output_widget("radiacion")),
            ui.nav_panel("Resultados", ui.output_text("pendiente")),
            ui.nav_panel("Datos", ui.output_data_frame("get_day_data"),
            ui.download_button("downloadData", "Download")),
            ui.nav_panel("Documentacion", ui.output_ui("documentacion")),

            title="Datos Gráficados",
        ),
    
    ui.include_css(app_dir / "styles.css"),
    title="Ener-Habitat Phy",
    fillable=True,
)

def server(input, output, session):
    #info_modal()
    
    @output
    @render.ui
    def left_controls():
        type = input.type()
        return controls_left(type, 
                        lugares, 
                        meses_dict, 
                        location, 
                        orientacion, 
                        Absortancia)

    @output
    @render.ui
    def ubicacion_orientacion():
        ubicacion = input.ubicacion()
        return orientacion_disable(ubicacion,  orientacion, Absortancia)
    
    @output
    @render.ui
    def absortancia_f():
        selected = input.absortancia()
        value = Absortancia.get(selected, 0.10)
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
    def temperatura():
        place = input.place()
        ruta_epw = ruta(place)
        mes = meses_dict[input.periodo()]
        caracteristicas = cargar_caracteristicas(place)
        absortancia = input.absortancia_value() #0.3
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
    def radiacion():
        place = input.place()
        ruta_epw = ruta(place)
        mes = meses_dict[input.periodo()]
        caracteristicas = cargar_caracteristicas(place)
        absortancia = input.absortancia_value() #0.3
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
        abs = input.absortancia()
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
            absortancia = Absortancia[input.absortancia()]  
            surface_tilt = location[input.ubicacion()] 
            surface_azimuth = orientacion[input.orientacion()]  
        
            result = data_frame(
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
            
            data_to_show = result[::3600].reset_index() 
            data_to_show['Fecha_Hora'] = data_to_show['Fecha_Hora'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return data_to_show 

    @render.download(
        filename=lambda: f"data-{date.today().isoformat()}.csv"
    )
    async def downloadData():
            place = input.place()
            ruta_epw = ruta(place)  
            mes = meses_dict[input.periodo()]  
            caracteristicas = cargar_caracteristicas(place) 
            absortancia = Absortancia[input.absortancia()]  
            surface_tilt = location[input.ubicacion()] 
            surface_azimuth = orientacion[input.orientacion()]  

            data = data_frame(
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
        
            data_= data[::3600].reset_index() 
            csv_buffer = StringIO()
            data_.to_csv(csv_buffer,index=True)
            csv_buffer.seek(0)

            await asyncio.sleep(0.25)
            yield csv_buffer.read()

    @output
    @render.ui
    def documentacion():
        modal_text = """
            Respiratory Diseases App

            Exploring Relationships between PM2.5 & Respiratory Diseases

            ----------------------------------------

            Problem Statement

            Air Pollution has always been a problem for the world and over
            the years, especially with the pandemic, the ambient air pollution
            seems to be a slow burn for the entire population of the planet.
            Through this app, we wish to explore the relationship between
            the PM2.5 particulate metric and the Death Rate
            (defined as deaths per 100,000) from respiratory
            illnesses over the world over the years.
            """
        return modal_text

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
