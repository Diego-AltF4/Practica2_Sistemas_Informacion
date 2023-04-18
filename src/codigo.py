import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as pl

def calculos_ej3(df, str):
    print("--- "+str+" ---")
    v = df["vulnerabilidades_detectadas"]
    print(f"Numero de observaciones: {len(v)}")
    count = 0
    for column in df:
        for i in df[column]:
            if i == "None":
                count += 1
    print(f"Numero de valores ausentes: {count}") #TODO
    #Mediana
    print(f"Mediana: {v.median()}")
    # Media
    print(f"Media: {v.mean()}")
    # Varianza
    print(f"Varianza: {v.var()}")
    # Valores maximo y minimo
    print(f"Valor maximo: {v.max()}")
    print(f"Valor minimo: {v.min()}")

conex = sqlite3.connect("Base-Datos.db")
cursor = conex.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY, timestamp TEXT, sid INTEGER, msg TEXT, clasificacion TEXT, prioridad INTEGER, protocolo TEXT, origen TEXT, destino TEXT, puerto INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS responsable (nombre TEXT PRIMARY KEY, telefono INTEGER, rol TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS analisis (id TEXT PRIMARY KEY, puertos_abiertos TEXT, n_puertos INTEGER, servicios INTEGER, servicios_inseguros INTEGER, vulnerabilidades_detectadas INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, ip TEXT, localizacion TEXT, responsable_id TEXT, analisis_id TEXT, FOREIGN KEY (responsable_id) REFERENCES responsable(nombre), FOREIGN KEY (analisis_id) REFERENCES analisis(id))")

with open ("datos_22_23/devices.json") as devicesJ:
    devices_json = json.load(devicesJ)

#Ejercicio 2
print("-------------------------------------------")
print("---------------EJERCICIO 2-----------------")
print("-------------------------------------------")
print()
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

contador = 0
alerts_csv = pd.read_csv("datos_22_23/alerts.csv")
alerts_csv.to_sql('alerts', conex, if_exists='replace', index=True, index_label="id")

dispositivos = pd.read_sql_query("SELECT * from devices", conex)
print(f"Numero de dispositivos: {len(dispositivos)}")
dispositivos = pd.read_sql_query("SELECT d.*, a.puertos_abiertos, a.n_puertos, a.servicios, a.servicios_inseguros, a.vulnerabilidades_detectadas, r.telefono, r.rol FROM devices AS d JOIN analisis AS a ON (d.analisis_id = a.id) JOIN responsable as r ON (d.responsable_id = r.nombre)", conex)
count = 0
for column in dispositivos:
    for i in dispositivos[column]:
        if i == "None":
            count += 1
print(f"Numero de campos None: {count}")

alertas = pd.read_sql_query("SELECT * from alerts", conex)
print(f"Numero de alertas: {len(alertas)}")

analisis_data = pd.read_sql_query("SELECT * from analisis", conex)
media = analisis_data['n_puertos'].mean()
desviacion = analisis_data['n_puertos'].std()
print(f"Media del total de puertos abiertos: {media:.4f}")
print(f"Desviacion estandar del total de puertos abiertos: {desviacion:.4f}")

media = analisis_data['servicios_inseguros'].mean()
desviacion = analisis_data['servicios_inseguros'].std()
print(f"Media del numero de servicios inseguros detectados: {media:.4f}")
print(f"Desviacion estandar del numero de servicios inseguros detectados: {desviacion:.4f}")

media = analisis_data['vulnerabilidades_detectadas'].mean()
desviacion = analisis_data['vulnerabilidades_detectadas'].std()
print(f"Media del numero de vulnerabilidades detectadas: {media:.4f}")
print(f"Desviacion estandar del numero de vulnerabilidades detectadas: {desviacion:.4f}")

minimo_npuertos = analisis_data['n_puertos'].min()
print(f"Valor minimo del total de puertos abiertos: {minimo_npuertos}")
maximo_npuertos = analisis_data['n_puertos'].max()
print(f"Valor maximo del total de puertos abiertos: {maximo_npuertos}")

minimo_vulnerabilidades_detectadas = analisis_data['vulnerabilidades_detectadas'].min()
print(f"Valor minimo del numero de vulnerabilidades detectadas: {minimo_vulnerabilidades_detectadas}")
maximo_vulnerabilidades_detectadas = analisis_data['vulnerabilidades_detectadas'].max()
print(f"Valor maximo del numero de vulnerabilidades detectadas: {maximo_vulnerabilidades_detectadas}")

# Ejercicio 3
print()
print("-------------------------------------------")
print("---------------EJERCICIO 3-----------------")
print("-------------------------------------------")
print()

vulns = pd.read_sql_query("SELECT al.prioridad, al.timestamp, d.*, an.puertos_abiertos, an.n_puertos, an.servicios, an.servicios_inseguros, an.vulnerabilidades_detectadas, r.telefono, r.rol FROM alerts AS al JOIN devices AS d ON (al.origen = d.ip OR al.destino = d.ip) JOIN analisis AS an ON (d.analisis_id = an.id) JOIN responsable as r ON (d.responsable_id = r.nombre)", conex)

calculos_ej3(vulns.loc[vulns['prioridad'] == 1], "Alertas de prioridad 1")
calculos_ej3(vulns.loc[vulns['prioridad'] == 2], "Alertas de prioridad 2")
calculos_ej3(vulns.loc[vulns['prioridad'] == 3], "Alertas de prioridad 3")

calculos_ej3(vulns.loc[pd.to_datetime(vulns['timestamp']).dt.month == 7], "Alertas de julio")
calculos_ej3(vulns.loc[pd.to_datetime(vulns['timestamp']).dt.month == 8], "Alertas de agosto")

# Ejercicio 4

ip_problematicas = pd.read_sql_query("SELECT origen, COUNT(*) AS n FROM alerts WHERE prioridad = 1 GROUP BY origen", conex)
ip_problematicas = ip_problematicas.sort_values('n', ascending=False)[:10]
pl.bar(ip_problematicas['origen'].to_numpy(), ip_problematicas['n'].to_numpy(), color="blue")
pl.xticks(rotation=45)
pl.xlabel("ip origen")
pl.ylabel("número de alertas")
pl.title("Las 10 IP de origen más problemáticas")
pl.show()

alertas_tiempo = pd.read_sql_query("SELECT timestamp, COUNT(*) AS n FROM alerts GROUP BY timestamp ORDER BY timestamp", conex)
alertas_tiempo['timestamp'] = pd.to_datetime(alertas_tiempo['timestamp']).dt.date
alertas_tiempo.groupby('timestamp').sum()
pl.plot(alertas_tiempo.get('timestamp').to_numpy(), alertas_tiempo.get('n').to_numpy(), color="blue")
pl.xticks(rotation=45)
pl.xlabel("timestamp")
pl.ylabel("número de alertas")
pl.title("Número de alertas en el tiempo")
pl.show()

alertas_clasificacion = pd.read_sql_query("SELECT clasificacion, COUNT(*) AS n FROM alerts GROUP BY clasificacion", conex)
pl.bar(alertas_clasificacion['clasificacion'].to_numpy(), alertas_clasificacion['n'].to_numpy(), color="blue")
pl.xticks(rotation=45)
pl.xlabel("categoría")
pl.ylabel("número de alertas")
pl.title("Número de alertas por categoría")
pl.show()

devices_vulns = pd.read_sql_query("SELECT d.id, a.servicios_inseguros+a.vulnerabilidades_detectadas as inseguridad FROM devices AS d JOIN analisis AS a ON (d.analisis_id = a.id)", conex)
devices_vulns = devices_vulns.sort_values('inseguridad', ascending=False)
pl.bar(devices_vulns['id'].to_numpy(), devices_vulns['inseguridad'].to_numpy(), color="blue")
pl.xticks(rotation=45)
pl.xlabel("dispositivo")
pl.ylabel("número de vulnerabilidades")
pl.title("Dispositivos más vulnerables")
pl.show()


puertos_servicios = pd.read_sql_query("SELECT AVG(n_puertos) AS numero_puertos, AVG(servicios) AS servicios_abiertos, AVG(servicios_inseguros) AS servicios_Inseguros FROM analisis", conex)
puertos_servicios1 = []
puertos_servicios1.append(puertos_servicios['numero_puertos'][0])
puertos_servicios1.append(puertos_servicios['servicios_abiertos'][0])
puertos_servicios1.append(puertos_servicios['servicios_Inseguros'][0])
fig, ax = pl.subplots()
ax.bar(list(puertos_servicios), puertos_servicios1, color="blue")
ax.set_xlabel("")
ax.set_ylabel("media")
ax.set_title("Puertos vs Servicios vs Servicios inseguros")
pl.show()

