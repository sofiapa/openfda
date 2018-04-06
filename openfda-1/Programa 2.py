#librerias de python para poder utilizar funciones ya creadas
import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?limit=10", None, headers) #ponemos limit=10 porque basandonos en el api así nos saldrá el id de 10 medicamentos
r1 = conn.getresponse() #respuesta del servidor
print(r1.status, r1.reason)
fichero_raw = r1.read().decode("utf-8") #el fichero es label.json
conn.close()

fichero = json.loads(fichero_raw) #interpreto el idioma json para que se me queden como listas y diccioanrios

for element in range (len (fichero['results'])):#recorro la lista de results del fichero json
    info_medicamento=fichero['results'][element]

    print ('ID: ',info_medicamento['id'])
