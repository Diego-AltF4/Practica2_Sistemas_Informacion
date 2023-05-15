import sqlite3
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd
import plotly.graph_objects as go
import plotly.utils as putil
import json
import requests


app = Flask(__name__)
app.config['VERSION'] = '1.0'


def getBBDD():
    conex = sqlite3.connect("Base-Datos.db")
    return conex


@app.route('/')
def hello_world():
    graphDir = direcciones()
    graphDev = dispositivos()
    services = servicios(True, 3)
    #cve = cves()
    return render_template('index.html', graphDir=graphDir, graphDev=graphDev, services=services)


@app.route('/direcciones', methods=['GET'])
def direcciones():
    rango = request.args.get("direcciones", default=10, type=int)
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
    return graphJSON


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
    return graphJSON


@app.route('/servicios/<rango>')
def servicios(rango):
    rango = int(rango)
    valorServicio = request.args.get('valorServicio', type=int)
    if valorServicio == 0:
        return servicios(False, rango)
    else:
        return servicios(True, rango)


def servicios(esMas, rango):
    devices_resultado = []
    conex = getBBDD()
    devices_peligro = pd.read_sql_query("SELECT d.id, d.ip, d.localizacion, a.servicios_inseguros, a.servicios FROM devices AS d JOIN analisis AS a ON (d.analisis_id = a.id)", conex)
    
    for i in range(len(devices_peligro['id'])):
        device = {'id': devices_peligro['id'][i], 'ip': devices_peligro['ip'][i], 'localizacion': devices_peligro['localizacion'][i], 'ratio': 0}

        if devices_peligro['servicios'][i] == 0:
            rate = 0
        else:
            rate = devices_peligro['servicios_inseguros'][i]/devices_peligro['servicios'][i]

        if esMas and rate > 0.33:
            device['ratio'] = round(rate, 3)
            devices_resultado.append(device)
        if not esMas and rate < 0.33:
            device['ratio'] = round(rate, 3)
            devices_resultado.append(device)

    devices_resultado = sorted(devices_resultado, key=lambda d: d['ratio'], reverse=esMas)[:rango]
    devices_json = json.dumps(devices_resultado)
    return devices_json


@app.route('/cves', methods=['GET'])
def cves():
    cves_resultado = []
    res = requests.get("https://cve.circl.lu/api/last").text
    data = json.loads(res)
    data = sorted(data, key=lambda d:d['Published'], reverse=True)[:10]

    for i in range(10):
        cve = {'id': data[i]["id"], 'published': data[i]["Published"], 'summary': data[i]["summary"].strip()[:107] + "..."}
        cves_resultado.append(cve)

    return cves_resultado

@app.route('/news', methods=['GET'])
def news():
    res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty").text.strip().replace('[','').replace(']','').split(',')
    noticias = []
    for i in range(30):
        id = int(res[i])
        res2 = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json?print=pretty").text
        data = json.loads(res2)
        noticia = {'title':data["title"],'url':data["url"].strip(),'by':data["by"]}
        noticias.append(noticia)

    return noticias

if __name__ == '__main__':
    app.run(debug=True)
