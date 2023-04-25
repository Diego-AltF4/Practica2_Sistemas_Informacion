import sqlite3
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd
import json
import plotly.graph_objects as go

app = Flask(__name__)
app.config['VERSION'] = '1.0'

def getBBDD():
    conex = sqlite3.connect("Base-Datos.db")
    return conex


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/direcciones', methods=['GET', 'POST'])
def direcciones():
    rango = request.args.get("direcciones", default=10, type=int)
    print(rango)
    conex = getBBDD()
    ip_problematicas = pd.read_sql_query("SELECT origen, COUNT(*) AS n FROM alerts WHERE prioridad = 1 GROUP BY origen", conex)
    ip_problematicas = ip_problematicas.sort_values('n', ascending=False)[:rango]
    fig = go.Figure(
        data=[go.Bar(x=ip_problematicas['origen'].to_numpy(), y=ip_problematicas['n'].to_numpy())],
    )
    fig.update_layout(legend_title_text="Diagrama de barras")
    fig.update_xaxes(title_text="IPs origen")
    fig.update_yaxes(title_text="Número de alertas")
    import plotly
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('template.html', graphJSON=graphJSON, x=rango, caso="problemáticas")

@app.route('/dispositivos', methods=['GET', 'POST'])
def dispositivos():
    rango = request.args.get('dispositivos', default=10, type=int)
    conex = getBBDD()

    devices_vulns = pd.read_sql_query("SELECT d.id, a.servicios_inseguros+a.vulnerabilidades_detectadas as inseguridad FROM devices AS d JOIN analisis AS a ON (d.analisis_id = a.id)", conex)
    devices_vulns = devices_vulns.sort_values('inseguridad', ascending=False)[:rango]

    fig = go.Figure(
        data=[go.Bar(x=devices_vulns['id'].to_numpy(), y=devices_vulns['inseguridad'].to_numpy())],
    )
    fig.update_layout(legend_title_text="Dispositivos más vulnerables")
    fig.update_xaxes(title_text="Dispositivos")
    fig.update_yaxes(title_text="Número de vulnerabilidades")
    import plotly
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('template.html', graphJSON=graphJSON, x=rango, caso=None)


if __name__ == '__main__':
    app.run(debug=True)
