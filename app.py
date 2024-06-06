from shiny import App, ui, render, reactive
from iertools.read import read_epw
import configparser
import pytz
from ehtools.diatipico import *
from ehtools.plot import *
from pathlib import Path

# Leer la configuración desde un archivo INI
config = configparser.ConfigParser()
config.read("lugares.ini")
lugares = config.sections()

configM = configparser.ConfigParser()
configM.read("materiales.ini")
materiales = configM.sections()

timezone = pytz.timezone('America/Mexico_City')
app_dir = Path(__file__).parent


def cargar_caracteristicas(lugar):
    lugar_config = config[lugar]
    return {
        "lat": lugar_config.getfloat('lat'),
        "lon": lugar_config.getfloat('lon'),
        "alt": lugar_config.getint('altitude'),
        "epw": lugar_config['f_epw']
    }
def ruta(lugar):
    f_epw = cargar_caracteristicas(lugar)
    epwP = f_epw['epw']
    divi = epwP.split("_")
    pa = divi[0].replace('data/', '')
    pais = pa.capitalize()
    es = divi[1]
    estado = es.capitalize()
    ciudad = divi[2].replace('.epw', '')
    ruta = f"./data/{pa}_{es}_{ciudad}.epw"
    return ruta
    
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
    "Techo": 0
}

orientacion = {
    "Norte": 0,
    "Noreste": 80,
    "Este": 90, 
    "Sureste": 140, 
    "Sur": 180,
    "Suroeste": 200, 
    "Oeste": 270, 
    "Noroeste": 290
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
                ui.input_numeric("abstraction", "Absortancia: ", value=0.1, min = 0.1, max = 1.0, step = 0.1),
            )
        elif input.type() == "2":
            return ui.TagList(
                ui.input_select("place", "Lugar:", choices=lugares),
                ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
                ui.input_select("option", "Ubicación:", choices=list(location.keys())),
                ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
                ui.input_numeric("abstraction", "Absortancia: ", value=0.1, min = 0.1, max = 1.0, step = 0.1),
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

        absortancia = 0.3
        surface_tilt = location[input.option()]  # ubicacion
        print(surface_tilt)
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
