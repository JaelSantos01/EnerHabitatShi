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
import pvlib
import math
import locale
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
        ui.card(
            ui.card_header("Gráfica"),
            ui.output_plot("grafica_mes"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Datos:"),
            ui.output_ui("datos_ui")
        ),
        col_widths=[10, 2],
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
                ui.input_select("ubicacion", "Ubicación:", choices=["Techo", "Muro"]),
                ui.input_select("orientacion", "Orientación:", choices=[
                    "Norte", "Noreste", "Este", "Sureste", "Sur",
                    "Suroeste", "Oeste", "Noroeste"
                ]),
                ui.input_numeric("inclinacion", "Inclinación:", value=0.1),
                ui.input_select("absortancia", "Absortancia(A):", choices=materiales),
            )
        elif input.type() == "2":
            return ui.TagList(
                ui.input_select("place", "Lugar:", choices=lugares),
                ui.input_selectize("periodo", "Mes:", choices=list(meses_dict.keys())),
                ui.input_select("option", "Ubicación:", choices=["Techo", "Muro"]),
                ui.input_select("orientacion", "Orientación:", choices=[
                    "Norte", "Noreste", "Este", "Sureste", "Sur",
                    "Suroeste", "Oeste", "Noroeste"
                ]),
                ui.input_select("absortancia", "Absortancia(A):", choices=materiales),
            )
        return None
    
    @output
    @render.ui
    def boxes():
        if input.type() == "1":
            return ui.layout_column_wrap(
                3,  # Número de columnas por fila
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
                ui.input_text(
                    "espesor",
                    "Espesor",
                    "  "
                ),
                ui.input_select(
                    "material",
                    "Materiales:",
                    choices= materiales
                ),
            )
        elif input.type() == "2":
            return ui.TagList(
                ui.input_select("muro", "Muro:", choices=materiales),
                ui.input_numeric("e11", "e11", value=0.1),
                ui.input_numeric("e21", "e21", value=0.1),
                ui.input_numeric("e12", "e12", value=0.1),
                ui.input_numeric("a11", "a11", value=0.1),
                ui.input_numeric("a21", "a21", value=0.1),
                ui.input_numeric("a12", "a12", value=0.1),
            )
        return None

    @output
    @render.plot
    def grafica_mes():
        place = input.place()
        ruta_epw = ruta(place)
        epw = read_epw(ruta_epw, year=2024, alias=True)
        mes = meses_dict[input.periodo()]

        caracteristicas = cargar_caracteristicas(place)
        lat = caracteristicas['lat']
        lon = caracteristicas['lon']
        alt = caracteristicas['alt']
        dia = '15'
        absortancia = 0.3
        h = 13.
        surface_tilt = 90  # Vertical
        surface_azimuth = 270

        f1 = f'2024-{mes}-{dia} 00:00'
        f2 = f'2024-{mes}-{dia} 23:59'
            
        dia = calculate_day(f1, f2, timezone, lat, lon, alt, place, epw, ruta_epw, mes, surface_tilt, surface_azimuth, absortancia, h)
        plot_T_I(dia)

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
