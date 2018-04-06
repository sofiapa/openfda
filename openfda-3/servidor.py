import http.server
import socketserver
import http.client
import json

PORT = 9995

#creamos una funcion que sirva como cliente porque coge los medicamentos de la pagina
#api.fda.gov y luego también de servidor ya que se los da esos medicamentos a nuestro
#propio servidor que estamos creando para que pueda mandarlo al cliente que se conecte
#a nuestro puerto
def medicamentos():
    lista = [] #creamos una lista vacía donde iremos añadiendo los medicamentos
    headers = {'User-Agent': 'http-client'}

    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", "/drug/label.json?limit=10", None, headers)

    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    fichero_raw = r1.read().decode("utf-8")
    conn.close()

    fichero = json.loads(fichero_raw)

    for i in range(len(fichero['results'])): #recorro la lista de results del fichero json
        info_medicamento = fichero['results'][i]
        if (info_medicamento['openfda']):#vemos si existe el diccionario openfda con contenido
            print('Fabricante: ', info_medicamento['openfda']['substance_name'][0])
            lista.append(info_medicamento['openfda']['substance_name'][0])
        else:
            lista.append("No disponible")

    return lista


#clase derivada de otra, concepto de herencia
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        # Colocamos las cabeceras necesarias para que el cliente entienda el
        # contenido que le enviamos (sera HTML)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        contenido=""" 
            <!doctype html>
            <html>
            <body style='background-color: #EDAAF9'>
                <h1>LOS 10 MEDICAMENTOS SON:</h1>
            </body>
            </html>
        """

        lista = medicamentos() #creamos una variable con lo que nos ha devuelto la funcion
        for element in lista:
            contenido += '<ul><li>'+element+'</li></ul>'

        self.wfile.write(bytes(contenido, "utf8"))
        return



# El servidor comienza a aqui
# objeto de nuestra propia clase
Handler = testHTTPRequestHandler

# Configurar el socket del servidor, para esperar conexiones de clientes
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

    # Entrar en el bucle principal
    # Las peticiones se atienden desde nuestro manejador
    # Cada vez que se ocurra un "GET" se invoca al metodo do_GET de
    # nuestro manejador

#Dejaremos el servidor siempre activo
try:
    httpd.serve_forever()

#Por si paramos el servidor
except KeyboardInterrupt:
    print("")
    print("Interrumpido por el usuario")

print("")
print("Servidor parado")
httpd.server_close()