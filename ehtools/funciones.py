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


def controls_left(type,lugares,meses_dict, location, orientacion,absortance):
    if type == "1":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.output_ui("ubicacion_orientacion")
        )
    elif type == "2":
        return ui.TagList(
            ui.input_select("place", "Lugar:", choices=lugares),
            ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
            ui.input_select("ubicacion", "Ubicación:", choices=list(location.keys())),
            ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
            ui.input_select("absortancia","Absortancia:", choices=list(absortance.keys())),
            ui.output_ui("absortancia_f"),
        )
    return None

def orientacion_disable(ubicacion,  orientacion, absortance):
    if ubicacion == "Techo":
        return ui.TagList(
                ui.input_select("absortancia", "Absortancia:", choices=list(absortance.keys())),
                ui.output_ui("absortancia_f")
            ) 
    else: 
        return ui.TagList(
                ui.input_select("orientacion", "Orientación:", choices=list(orientacion.keys())),
                ui.input_select("absortancia", "Absortancia:", choices=list(absortance.keys())),
                ui.output_ui("absortancia_f")
        )                  

def absortance_value(value):
        return ui.TagList(
            ui.input_numeric("absortancia_value", "", value=value, min=0.10, max=1.0)
        )

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
    if num > 5 or num < 1 or num is None:
        modal_content = "Solo se permiten hasta 5 sistemas constructivos."
        modal = ui.modal(modal_content, title="Error", easy_close=True)
        ui.modal_show(modal)
    
    else:
        num1 = ui.TagList(
            ui.layout_columns(
                ui.input_numeric("espesor1", "Espesor 1:", value=0.010, max=0.9, step=0.01, min=0.010),
                ui.input_select("material1", "Material 1:", choices=materiales)
            )
        )
        
        num2 = ui.TagList(
            ui.layout_columns(
                ui.input_numeric("espesor2", "Espesor 2:", value=0.010, max=0.9, step=0.01, min=0.010),
                ui.input_select("material2", "Material 2:", choices=materiales)
            )
        )
        
        num3 = ui.TagList(
            ui.layout_columns(
                ui.input_numeric("espesor3", "Espesor 3:", value=0.010, max=0.9, step=0.01, min=0.010),
                ui.input_select("material3", "Material 3:", choices=materiales)
            )
        )
        
        num4 = ui.TagList(
            ui.layout_columns(
                ui.input_numeric("espesor4", "Espesor 4:", value=0.010, max=0.9, step=0.01, min=0.010),
                ui.input_select("material4", "Material 4:", choices=materiales)
            )
        )
        
        num5 = ui.TagList(
            ui.layout_columns(
                ui.input_numeric("espesor5", "Espesor 5:", value=0.010, max=0.9, step=0.01, min=0.010),
                ui.input_select("material5", "Material 5:", choices=materiales)
            )
        )
        
        if num == 1:
            return num1
        elif num == 2:
            return num1 + num2
        elif num == 3:
            return num1 + num2 + num3
        elif num == 4:
            return num1 + num2 + num3 + num4
        elif num == 5:
            return num1 + num2 + num3 + num4 + num5

