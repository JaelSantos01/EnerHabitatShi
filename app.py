from shiny import App, ui, render, reactive
import pytz
from ehtools.diatipico import *
from ehtools.plot import *
from pathlib import Path
from ehtools.funciones import *

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

abstraccion = {
    "Acero" : 0.45,
    "Aluminio oxidado": 0.15,
    "Aluminio pulido": 0.1,
    "Asfalto nuevo": 0.95,
    "Concreto": 0.7,
    "Concreto claro o adocreto claro": 0.6,
    "Impermeabilizante o pintura blanca": 0.2,
    "Impermeabilizante o pintura blanca nueva": 0.15,
    "Impermeabilizante o pintura negra": 0.9,
    "Impermeabilizante o pintura negra mate nueva": 0.95,
    "Impermeabilizante rojo terracota": 0.7,
    "Ladrillo rojo": 0.65,
    "Lámina galvanizada": 0.7,
    "Lámina galvanizada brillante": 0.25,
    "Pintura aluminio": 0.2,
    "Pintura colores claros": 0.3,
    "Pintura colores intermedios": 0.5,
    "Pintura colores oscuros": 0.7,
    "Recubrimiento elastomérico blanco": 0.3,
    "Teja roja": 0.7,
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("left_controls"),
    ),
        ui.layout_column_wrap(
            ui.layout_columns(
                ui.output_ui("controls_top"),
            ),
        
                ui.value_box(
                    "Tipo de sistema:",
                    ui.input_select(  
                        "type",  
                        "",  
                        {"1": "Capa homogénea", "2": "Modelo 2D"},  
                    ),
                ),

        ),
    ui.layout_columns(
        ui.navset_card_underline(
            ui.nav_panel("Gráfica", ui.output_plot("grafica_mes")),
            ui.nav_panel("Resultados", ui.output_plot("pendiente")),
            title="Datos Gráficados",
        ),
        ui.card(
            ui.card_header("Datos:"),
            ui.output_ui("controls_rigth")
        ),
        col_widths=[9, 3],
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
                    abstraccion)
    
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
    @render.plot
    def grafica_mes():
        place = input.place()
        ruta_epw = ruta(place)
        # epw = read_epw(ruta_epw, year=2024, alias=True)
        mes = meses_dict[input.periodo()]

        caracteristicas = cargar_caracteristicas(place)

        absortancia = abstraccion[input.abstrac()] #0.3
        surface_tilt = location[input.ubicacion()]  # ubicacion
        #print(surface_tilt)
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
        
        plot_T_I(dia)


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
