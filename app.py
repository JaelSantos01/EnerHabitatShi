import pandas as pd
from shiny import App, ui, render
from shinywidgets import render_widget
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo (puedes reemplazar esto con tus propios datos)
data = {
    "tiempo": [],
    "temperatura": [],
    "mes": [],
    "place": []
}

# Definir los tiempos comunes a todos los meses
tiempos_comunes = [24, 6, 12, 18, 24]

# Definir los meses y lugares
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']
lugares = ['Acapulco Gro.', 'Aguascalientes, Ags.', 'Veracruz, Ver.', 'Temixco, Mor.', 'Bogotá, Colombia']

# Generar datos para cada mes y lugar
for mes in meses:
    for lugar in lugares:
        # Generar temperaturas aleatorias para cada tiempo común
        for tiempo in tiempos_comunes:
            # Agregar temperatura y tiempo
            data["tiempo"].append(tiempo)
            data["temperatura"].append(np.random.randint(20, 35))  # Temperatura aleatoria entre 20 y 35 grados
            data["mes"].append(mes)
            data["place"].append(lugar)

df = pd.DataFrame(data)

print(df)

# Definir la interfaz de usuario
app_ui = ui.page_fluid(
    ui.panel_title("Ener-Habitat Phy"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "place",
                "Lugar:",
                choices=["Acapulco Gro.", "Aguascalientes, Ags.", "Veracruz, Ver.", "Temixco, Mor.", "Bogotá, Colombia",
                         "Buenos Aires, Argentina"]
            ),
            ui.input_selectize(
                "periodo",
                "Periodo:",
                choices=["Anual", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
                         "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            ),
            ui.input_select(
                "conditional",
                "Condición:",
                choices=["Sin aire acondicionado", "Con aire acondicionado"]
            )
        ),
        ui.panel_main(
            ui.output_plot("line_plot")
        )
    )
)

# Definir la lógica del servidor
def server(input, output, session):
    @output
    @render.plot
    def line_plot():
        selected_place = input.place()
        selected_period = input.periodo()
        filtered_df = df[df['place'] == selected_place]

        if selected_period != "Anual":
            filtered_df = filtered_df[filtered_df['mes'] == selected_period]

        # Crear el gráfico de barras
        plt.figure()
        ax = sns.barplot(data=filtered_df, x="tiempo", y="temperatura")
        ax.set_title(f"{selected_period}")
        ax.set_xlabel("Tiempo [h]")
        ax.set_ylabel("Temperatura [°C]")
        return plt.gcf()

# Crear la aplicación
app = App(app_ui, server)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run()
