import sqlite3
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.utils as putil

app = Flask(__name__)
app.config['VERSION'] = '1.0'

def getBBDD():
    conex = sqlite3.connect("Base-Datos.db")
    return conex


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/direcciones', methods=['GET'])
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
    graphJSON = json.dumps(fig, cls=putil.PlotlyJSONEncoder)
    return render_template('template.html', graphJSON=graphJSON, x=rango, caso="problemáticas")

@app.route('/dispositivos', methods=['GET'])
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
    graphJSON = json.dumps(fig, cls=putil.PlotlyJSONEncoder)
    return render_template('template.html', graphJSON=graphJSON, x=rango, caso=None)

@app.route('/servicios', methods=['GET'])
def servicios():
    rango = request.args.get('servicios', default=10, type=int)
    valorServicio = request.args.get('valorServicio', type=int)
    if valorServicio == 0:
        servicios(False, rango)
    else:
        servicios(True, rango)

def servicios(esMas, rango):
    conex = getBBDD()

    devices_peligro = pd.read_sql_query("SELECT d.id, d.ip, d.localizacion, a.servicios_inseguros, a.servicios FROM devices AS d JOIN analisis AS a ON (d.analisis_id = a.id)", conex)
    print(devices_peligro)

    devices_resultado = []
    for i in range(len(devices_peligro['id'])):
        device = {'id':devices_peligro['id'][i],'ip':devices_peligro['ip'][i],'localizacion':devices_peligro['localizacion'][i],'ratio':0}

        if devices_peligro['servicios'][i] == 0:
            rate = 0
        else:
            rate = devices_peligro['servicios_inseguros'][i]/devices_peligro['servicios'][i]
        if esMas and rate>0.33:
            device['ratio'] = rate
            devices_resultado.append(device)
        if not esMas and rate<0.33:
            device['ratio'] = rate
            devices_resultado.append(device)
    
    devices_resultado = sorted(devices_resultado, key=lambda d:d['ratio'], reverse=esMas)[:rango]

    print(devices_resultado)

    return render_template('template.html', graphJSON=graphJSON, x=rango, caso=None) #TODO




if __name__ == '__main__':
    app.run(debug=True)
