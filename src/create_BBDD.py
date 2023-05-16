import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as pl

conex = sqlite3.connect("Base-Datos.db")
cursor = conex.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY, timestamp TEXT, sid INTEGER, msg TEXT, clasificacion TEXT, prioridad INTEGER, protocolo TEXT, origen TEXT, destino TEXT, puerto INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS responsable (nombre TEXT PRIMARY KEY, telefono INTEGER, rol TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS analisis (id TEXT PRIMARY KEY, puertos_abiertos TEXT, n_puertos INTEGER, servicios INTEGER, servicios_inseguros INTEGER, vulnerabilidades_detectadas INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, ip TEXT, localizacion TEXT, responsable_id TEXT, analisis_id TEXT, FOREIGN KEY (responsable_id) REFERENCES responsable(nombre), FOREIGN KEY (analisis_id) REFERENCES analisis(id))")

with open ("datos_22_23/devices.json") as devicesJ:
    devices_json = json.load(devicesJ)

contador = 0
for it in devices_json:
    puertos_abiertos_raw = it['analisis']['puertos_abiertos']
    n_puertos = len(puertos_abiertos_raw)
    puertos_abiertos = ""
    if puertos_abiertos_raw == "None":
        puertos_abiertos = puertos_abiertos_raw
        n_puertos = 0
    else:
        for i in range(n_puertos):
            puertos_abiertos += str(puertos_abiertos_raw[i])
            if i != n_puertos - 1:
                puertos_abiertos += '|'
    servicios = it['analisis']['servicios']
    servicios_inseguros = it['analisis']['servicios_inseguros']
    vulnerabilidades_detectadas = it['analisis']['vulnerabilidades_detectadas']
    cursor.execute("INSERT OR IGNORE INTO analisis (id, puertos_abiertos, n_puertos, servicios, servicios_inseguros, vulnerabilidades_detectadas) VALUES (?, ?, ?, ?, ?, ?)", (contador, puertos_abiertos, n_puertos, servicios, servicios_inseguros, vulnerabilidades_detectadas))


    nombre_responsable = it['responsable']['nombre']
    telefono_responsable = it['responsable']['telefono']
    rol_responsable = it['responsable']['rol']
    cursor.execute("INSERT OR IGNORE INTO responsable (nombre, telefono, rol) VALUES (?, ?, ?)", (nombre_responsable, telefono_responsable, rol_responsable))

    device_id = it['id']
    device_ip = it['ip']
    device_localizacion = it['localizacion']

    cursor.execute("INSERT OR IGNORE INTO devices (id, ip, localizacion, responsable_id, analisis_id) VALUES (?, ?, ?, ?, ?)", (device_id, device_ip, device_localizacion, nombre_responsable, contador))

    contador += 1

alerts_csv = pd.read_csv("datos_22_23/alerts.csv")
alerts_csv.to_sql('alerts', conex, if_exists='replace', index=True, index_label="id")
