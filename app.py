import plotly.express as px
import pandas as pd
from shiny import App, ui, render
from shinywidgets import render_widget
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from iertools.read import read_epw
from dateutil.parser import parse 
import configparser

# Leer la configuración desde un archivo INI
config = configparser.ConfigParser()
config.read("lugares.ini")
lugares = config.sections()

#ruta = './data/Casablanca.epw'
#zaca = './data/MEX_MOR_Zacatepec.epw'
#cuerna = './data/MEX_MOR_Cuernavaca.epw'
dia = "15"
#read_epw(ruta) #Visualiza el documento que tiene la ruta


def cargar_caracteristicas(lugar):
    lugar_config = config[lugar]
    return {
        "lat": lugar_config.getfloat('lat'),
        "lon": lugar_config.getfloat('lon'),
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

#def carga_epw(ruta_epw):
#    epw = read_epw(ruta_epw, alias=True, year=2024)
#    return epw


app_ui = ui.page_fluid(
    ui.panel_title("Ener-Habitat Phy"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "place",
                "Lugar:",
                choices= lugares
            ),
            ui.input_selectize(
                "periodo",
                "Periodo:",
                choices=list(meses_dict.keys())
            ),
            ui.input_select(
                "Conditional",
                "Condición:",
                choices=["Sin aire acondicionado", "Con aire acondicionado"]
            )
        ),
        ui.panel_main(
            ui.output_plot("grafica_mes"),
            ui.output_text("caracteristicas")
        )
    )
)


def server(input, output, session):
    @output
    @render.plot
    def grafica_mes():
        #Dependiendo el lugar toma el epw
        place = input.place()
        ruta_epw = ruta(place)
        epw = read_epw(ruta_epw, year=2024, alias=True)
        mes = meses_dict[input.periodo()]
        fig, ax = plt.subplots(2, figsize=(10, 3), sharex=True)
        f1 = parse(f"2024-{mes}-{dia}")
        f2 = f1 + pd.Timedelta("7D")

        ax[0].plot(epw.To, label="Ta")
        ax[1].plot(epw.Ig, label="Ig")
        ax[1].plot(epw.Ib, label="Ib")
        ax[1].plot(epw.Id, label="Id")

        ax[0].set_xlim(f1, f2)
        ax[0].legend()
        ax[1].legend()
        return fig

    @output
    @render.text
    def caracteristicas():
        lugar = input.place()
        caracteristicas = cargar_caracteristicas(lugar)
        lat = caracteristicas['lat']
        lon = caracteristicas['lon']
        epw = caracteristicas['epw']
        return f"Latitud: {lat}, Longitud: {lon}, EPW: {epw}"
    
# Crear la aplicación de Shiny
app = App(app_ui, server)

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run()
