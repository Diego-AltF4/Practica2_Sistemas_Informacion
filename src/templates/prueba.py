import json

import requests

cves_resultado = []
res = requests.get("https://cve.circl.lu/api/last").text
data = json.loads(res)
data = sorted(data, key=lambda d:d['Published'], reverse=True)[:10]

for i in range(10):
    cve = {'id': data[i]["id"], 'published': data[i]["Published"], 'summary': data[i]["summary"].strip()[:97] + "..."}
    cves_resultado.append(cve)

print(cves_resultado)
