import http.client
import json

headers = {'User-Agent': 'http-client'}

#hacemos un bucle infinito para no saltarnos ningun fabricante
while True:

    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", '/drug/label.json?limit=100&search=active_ingredient:"acetylsalicylic"', None, headers)
    #ponemos de limit 100 porque es el máximo que podemos poner
    r1 = conn.getresponse()  # respuesta del servidor
    print(r1.status, r1.reason)
    fichero_raw = r1.read().decode("utf-8")  # el fichero es label.json
    conn.close()

    fichero = json.loads(fichero_raw)  # interpreto el idioma json para que se me queden como listas y diccioanrios

    for element in range (len(fichero['results'])): #recorro la lista de results del fichero json
        info_medicamento=fichero['results'][element]

        if (info_medicamento['openfda']): #vemos si existe el diccionario openfda con contenido
            print ('FABRICANTE:',[element], info_medicamento['openfda']['manufacturer_name'][0])
        else:
            print ("FABRICANTE NO DISPONIBLE")

    if (len(fichero['results']))<100:
        break
    #si la longitud de la lista results es menor que cien paramos el bucle infinito, ya que
    #no nos sirve de nada que siga funcionando porque si la longitus es menor que cien no
    #nos van a salir mas fabricantes

