import configparser
from shiny import App, ui, render, reactive
from iertools.read import read_epw

# Leer la configuración desde un archivo INI
config = configparser.ConfigParser()
config.read("lugares.ini")
lugares = config.sections()

configM = configparser.ConfigParser()
configM.read("materiales.ini")
materiales = configM.sections()

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

def controls_left(type,lugares,meses_dict, location, orientacion,abstraccion):
    if type == "1":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
            ui.input_select("abstrac","Absortancia:", choices=abstraccion),
        )
    elif type == "2":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
            ui.input_select("abstrac","Absortancia:", choices=abstraccion),
        )
    return None

def top_controls(type):
    if type == "1":
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
    elif type == "2":
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

def rigth_controls(type, materiales):
    if type == "1":
        return ui.TagList(
            ui.output_ui("campos")
        )
    elif type == "2":
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


def info_right(num, materiales):
    campos_list = []
    for i in range(num):
        campos_list.append(
            ui.TagList(
                ui.layout_columns(
                    ui.input_numeric(f"espesor_{i}", f"Espesor {i+1}:", value=0.1),
                    ui.input_select(f"materiales_{i}", f"Material {i+1}:", choices=materiales)
                )
            )
        )
    return campos_list