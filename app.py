from shiny import App, ui, render, reactive
from iertools.read import read_epw
import configparser
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
        ui.input_radio_buttons(
            "type",
            "Sistema a realizar:",
            {"1": "Capa homogénea", "2": "Modelo 2D"},
        ),
        ui.output_ui("additional_controls"),
    ),
            ui.output_ui("boxes"),
    ui.layout_columns(
        ui.navset_card_underline(
            ui.nav_panel("Gráfica", ui.output_plot("grafica_mes")),
            ui.nav_panel("Resultados", ui.output_plot("pendiente")),
            title="Datos Gráficados",
        ),
        ui.card(
            ui.card_header("Datos:"),
            ui.output_ui("datos_ui")
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
    def additional_controls():
        if input.type() == "1":
            return ui.TagList(
                ui.input_select("place", "Lugar:", choices=lugares),
                ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
                ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
                ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
                ui.input_select("abstrac","Absortancia:", choices=abstraccion),
            )
        elif input.type() == "2":
            return ui.TagList(
                ui.input_select("place", "Lugar:", choices=lugares),
                ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
                ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
                ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
                ui.input_select("abstrac","Absortancia:", choices=abstraccion),
            )
        return None
    
    @output
    @render.ui
    def boxes():
        if input.type() == "1":
            return ui.layout_column_wrap(
                3,# Número de columnas por fila
                ui.value_box(
                    "Número de Sistemas:",
                    ui.input_slider("sistemas", "", 1, 5, 1),
                ),
                ui.value_box(
                    "Condición:",
                    ui.input_select("Conditional", "", choices=["Sin aire acondicionado", "Con aire acondicionado"]),
                ),
            )
        elif input.type() == "2":
            return ui.layout_column_wrap(
                3,  # Número de columnas por fila
                ui.value_box(
                    "Número de Capas:",
                    ui.input_slider("capas", "", 1, 5, 1),
                ),
                ui.value_box(
                    "Condición:",
                    ui.input_select("Conditional", "", choices=["Sin aire acondicionado", "Con aire acondicionado"]),
                ),
            )
        return None
    
    @output
    @render.ui
    def datos_ui():
        if input.type() == "1":
            return ui.TagList(
                ui.output_ui("campos")
            )
        elif input.type() == "2":
            return ui.TagList(
                ui.HTML('<img src="http://www.enerhabitat.unam.mx/Cie/images/Muro-tipo1-modelo1.png" width="320" height="150">'),
                ui.input_select("muro", "Muro:", choices=materiales),
                ui.layout_columns(
                    ui.input_numeric("e11", "e11", value=0.1),
                    ui.input_numeric("a11", "a11", value=0.1),
                ),
                ui.layout_columns(
                    ui.input_numeric("e21", "e21", value=0.1),
                    ui.input_numeric("a21", "a21", value=0.1),
                ),
                ui.layout_columns(
                    ui.input_numeric("e12", "e12", value=0.1),
                    ui.input_numeric("a12", "a12", value=0.1),
                ),
            )
        return None

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

    @output
    @render.ui
    def campos():
        num = input.sistemas()
        i = 0
        
        campos_list = []
        while i < num:
            campos_list.append(
                ui.TagList(
                    ui.layout_columns(
                        ui.input_numeric(f"espesor_{i}", f"Espesor {i+1}:", value=0.1),
                        ui.input_select(f"materiales_{i}", f"Material {i+1}:", choices=materiales)
                    ),
                )
            )
            i = i + 1
        return campos_list


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
