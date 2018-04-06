import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov") #establezco canal de comunicación
conn.request("GET", "/drug/label.json", None, headers) #manda¡o una peticion al servidor, el recurso
r1 = conn.getresponse() #respuesta del servidor
print(r1.status, r1.reason)
fichero_raw = r1.read().decode("utf-8") #el fichero es label.json
conn.close()

fichero = json.loads(fichero_raw) #interpreto el idioma json para que se me queden como listas y diccioanrios

print ('ID:',fichero['results'][0]['id'])
print ('PROPÓSITO:',fichero['results'][0]['purpose'][0])
print ('FABRICANTE:',fichero['results'][0]['openfda']['manufacturer_name'][0])

