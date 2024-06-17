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
    valor_inicial = list(abstraccion.values())[0]
    if type == "1":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
            ui.input_select("abstrac","Absortancia:", choices=list(abstraccion.keys())),
            ui.input_numeric("abstrac_numeric", "Absortancia:", value = valor_inicial),
        )
    elif type == "2":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
            ui.input_select("abstrac","Absortancia:", choices=list(abstraccion.keys())),
            ui.input_numeric("abstrac_numeric", "Absortancia:", value = valor_inicial),
        )
    return None

def top_controls(type):
    if type == "1":
        return ui.TagList(
            ui.input_numeric("sistemas", "Número de sistemas:", value=1, min=1, max=5),  
            ui.input_select("Conditional", "Condición:", choices=["Sin aire acondicionado", "Con aire acondicionado"]),  
        )
    elif type == "2":
        return ui.TagList(
            ui.input_slider("capas", "Número de capas:", 1, 5, 1),
            ui.input_select("Conditional", "Condición:", choices=["Sin aire acondicionado", "Con aire acondicionado"]),
        )
    return None



def rigth_controls(type, materiales):
    if type == "1":
        return ui.TagList(
            ui.output_ui("campos")
        )
    elif type == "2":
        return ui.TagList(
            ui.HTML('<img src="http://www.enerhabitat.unam.mx/Cie/images/Muro-tipo1-modelo1.png" width="200" height="90">'),
            ui.input_select("muro", "Material:", choices=materiales),
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
    if num > 5 or num < 1:
        modal_content = "Solo se permiten hasta 5 sistemas constructivos."
        modal = ui.modal(modal_content, title="Error", easy_close=True)
        ui.modal_show(modal)
    else:
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

