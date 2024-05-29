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
from matplotlib.dates import ConciseDateFormatter, AutoDateLocator
import pytz
from ehtools.diatipico import *

# Leer la configuración desde un archivo INI
config = configparser.ConfigParser()
config.read("lugares.ini")
lugares = config.sections()

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
            ),
            ui.input_select(
                "option",
                "Ubicación:",
                choices=["Techo", "Muro"]
            ),
            ui.input_slider(
                "rango",
                "Número de Sistemas:",
                1,5,1
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

        caracteristicas = cargar_caracteristicas(place)
        lat = caracteristicas['lat']
        lon = caracteristicas['lon']
        alt = caracteristicas['alt']

        dia = '15'
        absortancia = 0.3
        h = 13.
        # Parámetros de la superficie
        surface_tilt = 90  # Vertical
        surface_azimuth = 270  #
        timezone = pytz.timezone('America/Mexico_City')

        if surface_tilt == 0:
            LWR = 3.9
        else:
            LWR = 0.

        f1 = f'2024-{mes}-{dia} 00:00'
        f2 = f'2024-{mes}-{dia} 23:59'
        
        dia = pd.date_range(start=f1, end=f2, freq='1s',tz=timezone)
        location = pvlib.location.Location(latitude = lat, 
                                        longitude=lon, 
                                        altitude=alt,
                                        tz=timezone,
                                        name=place)

        dia = location.get_solarposition(dia)
        del dia['apparent_zenith']
        del dia['apparent_elevation']

        sunrise,_ = get_sunrise_sunset_times(dia)
        tTmax,Tmin,Tmax = calculate_tTmaxTminTmax(ruta_epw,mes,epw)
        
        # # Calcular la temperatura ambiente y agregarla al DataFrame
        dia = temperature_model(dia, Tmin, Tmax, sunrise, tTmax)
        # # Agrega Ig, Ib, Id a dia 

        dia = add_IgIbId_Tn(ruta_epw,dia,epw,mes,f1,f2,timezone)

        total_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth,
            dni=dia['Ib'],
            ghi=dia['Ig'],
            dhi=dia['Id'],
            solar_zenith=dia['zenith'],
            solar_azimuth=dia['azimuth']
        )
        dia['Is'] = total_irradiance.poa_global
        dia['Tsa'] = dia.Ta + dia.Is*absortancia/h - LWR
        DeltaTa= dia.Ta.max() - dia.Ta.min()

        dia['DeltaTn'] = calculate_DtaTn(DeltaTa)

        fig, ax = plt.subplots(2,figsize=(10,6),sharex=True)

        df = dia.iloc[::600]
        ax[0].plot(df.Ta, 'k-',label='Ta')
        # ax[0].plot(df.Tn, 'g-',label='Tn')
        ax[0].plot(df.Tsa,'r-',label='Tsa')
        ax[0].fill_between(df.index,
                        df.Tn + df.DeltaTn,
                        df.Tn - df.DeltaTn,color='green',alpha=0.3)

        ax[1].plot(df.Ig,label='Ig')
        ax[1].plot(df.Ib,label='Ib')
        ax[1].plot(df.Id,label='Id')
        ax[1].plot(df.Is,label='Is')

        ax[0].set_ylabel('Temperatura [$^oC$]')
        ax[1].set_ylabel('Irradiancia [$W/m^2$]')

        locator = AutoDateLocator()
        formatter = ConciseDateFormatter(locator)
        ax[1].xaxis.set_major_formatter(formatter)


        for a in ax:
            a.legend()
            a.grid()
        fig.tight_layout()

        return fig

    @output
    @render.text
    def caracteristicas():
        lugar = input.place()
        caracteristicas = cargar_caracteristicas(lugar)
        lat = caracteristicas['lat']
        lon = caracteristicas['lon']
        alt = caracteristicas['alt']
        epw = caracteristicas['epw']
        return f"Latitud: {lat}, Longitud: {lon}, Altitud: {alt}, EPW: {epw}"
    
# Crear la aplicación de Shiny
app = App(app_ui, server)

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run()
