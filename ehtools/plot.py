import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_T_I(dia):
    # Crear una figura con subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    # Datos filtrados
    df = dia.iloc[::600]

    # Subplot 1: Temperaturas y área sombreada
    fig.add_trace(go.Scatter(x=df.index, y=df['Ta'], mode='lines', name='Ta', line=dict(color='black')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Tsa'], mode='lines', name='Tsa', line=dict(color='red')), row=1, col=1)
    # Las áreas sombreadas en plotly pueden ser añadidas usando 'fill' en go.Scatter
    fig.add_trace(go.Scatter(x=df.index, y=df['Tn'] + df['DeltaTn'], mode='lines',showlegend=False , line=dict(color='rgba(0,0,0,0)')),
                row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Tn'] - df['DeltaTn'], mode='lines',showlegend=False , fill='tonexty', line=dict(color='rgba(0,0,0,0)'), fillcolor='rgba(0,255,0,0.3)'),
                row=1, col=1)

    # Subplot 2: Irradiancia
    fig.add_trace(go.Scatter(x=df.index, y=df['Ig'], mode='lines', name='Ig'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Ib'], mode='lines', name='Ib'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Id'], mode='lines', name='Id'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Is'], mode='lines', name='Is'), row=2, col=1)

    # Configuración adicional
    fig.update_layout(height=800, width=1000)
    fig.update_yaxes(title_text="Temperatura [°C]", row=1, col=1)
    fig.update_yaxes(title_text="Irradiancia [W/m²]", row=2, col=1)

    # Mostrar figura
    return fig