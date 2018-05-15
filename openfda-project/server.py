
import http.server
import http.client
import json
import socketserver

PORT=8000

# Clase derivada de otra, concepto de herencia
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    API_URL="api.fda.gov"
    API_PETICION="/drug/label.json"
    API_DRUG='&search=active_ingredient:'
    API_COMPANY='&search=openfda.manufacturer_name:'

# Hacemos tres funciones auxiliares
    #La primera nos crea la pagina web principal con el formulario, un html
    def pag_principal(self):
        html = """
            <html>
                <head>
                    <title>Aplicacion OpenFDA</title>
                </head>
                <body style='background-color: #EDAAF9'>
                    <h1>Busca en "Drug product labelling"</h1>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Drug List">
                        </input>
                    </form>
                    _______________________________________
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Drug Search">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                   _______________________________________
                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Company List">
                        </input>
                    </form>
                    _______________________________________
                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Company Search">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    _______________________________________
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Warnings List">
                        </input>
                    </form>
                </body>
            </html>
                """
        return html

    # LA segunda funcion nos crea las paginas web, html, para cada recurso
    def recurso_web (self, lista):
        list_html = """
                                <html>
                                    <head>
                                        <title>OpenFDA Cool App</title>
                                    </head>
                                    <body>
                                        <ul>
                            """
        for item in lista:
            list_html += "<li>" + item + "</li>"

        list_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return list_html

    # Y la tercera se conecta a openfda y se descarga y nos guarda toda la información del recurso pedido "/drug/label.json"
    # en un fichero label.son el que luego tambien decodifica para que podamos entenderlo
    def todos_resultados (self, limit=10):
        conn = http.client.HTTPSConnection(self.API_URL)
        conn.request("GET", self.API_PETICION + "?limit="+str(limit))
        print (self.API_PETICION + "?limit="+str(limit))
        r1 = conn.getresponse()
        fichero_raw = r1.read().decode("utf8")
        fichero = json.loads(fichero_raw)
        resultados = fichero['results']
        return resultados

#Función principal del programa que manda peticiones a openfda, de lo que el cliente le ha solicitado
    def do_GET(self):

        #Primero ve si en la peticiones del cliente hay o no parametros
        lista_recurso = self.path.split("?")
        if len(lista_recurso) > 1:
            params = lista_recurso[1]
        else:
            params = ""

        limit = 1 #Si no hay parámetros ponemos el de limit=1 por defecto

        #Obtenemos los parámetros
        if params:
            splitted_params = params.split("=")
            if splitted_params[0] == "limit":
                limit = int(splitted_params[1])
        else:
            print("No se encuentran parámetros")



# A continuación veremos los diferentes tipos de recursos que nos pueden pedir en las peticiones

        # Si el recurso es "/" hacemos que nos lleve a la pagina principal donde está el formulario
        if self.path=="/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_pag_principal=self.pag_principal() #Guardamos en una variable la funcion que nos crea la pagina principal
            self.wfile.write(bytes(html_pag_principal, "utf8"))

        # En los tres siguientes recursos hay que devolver una lista de medicamentos, empresas y advertencias
        # Primero creamos una lista vacía, luego añadiremos a una variable la lista de todos los resultados que
        # hemos obtenido por la función todos_resultados y los analizaremos viendo si el medicamento, empresa o
        # advertencia que nos han pedido esta en openfda; y si está lo añadiremos a la lista vacía que habíamos
        #creado y sino pues pondremos que es desconocido. Por último crearemos una variable para guardar la
        #funcion que nos crea esa página web donde saldra nuestra lista de medicamentos, empresas o advertencias.

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            medicamentos = []
            resultados = self.todos_resultados(limit)
            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append (resultado['openfda']['generic_name'][0])
                else:
                    medicamentos.append('Desconocido')
            listDrugs_html = self.recurso_web (medicamentos)
            self.wfile.write(bytes(listDrugs_html, "utf8"))

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            empresas = []
            resultados = self.todos_resultados (limit)
            for resultado in resultados:
                if ('manufacturer_name' in resultado['openfda']):
                    empresas.append (resultado['openfda']['manufacturer_name'][0])
                else:
                    empresas.append('Desconocido')
            listCompanies_html = self.recurso_web(empresas)
            self.wfile.write(bytes(listCompanies_html, "utf8"))

        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            advertencias = []
            resultados = self.todos_resultados(limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    advertencias.append (resultado['warnings'][0])
                else:
                    advertencias.append('Desconocido')
            listWarnings_html = self.recurso_web(advertencias)
            self.wfile.write(bytes(listWarnings_html, "utf8"))

        # Para los dos siguientes recursos, nos pediran un medicamento o una empresa en concreto y
        # debemos devolver información que tenga OpenFDA acerca de ello.Primero ponemos un limit=10,
        # después separamos el recurso y parámetro por el = y en la posicion uno nos quedara el
        # medicamento o la compañía por la que nos preguntan. A continuacion crearemos una conexion
        # con openfda para sacar todos los resultados ya que no podemos usar la funcion todos_resultados
        # porque aqui te piden un parámetro específico o un medicamento especifico o una empresa específica.
        # Esto lo tenemos en cuenta a la hora de hacer la petición a OpenFDA ya que le tenemos que mandar ese
        # parámetro específico al recurso de API_PETICION. Una vez obtenidos los resultados de la petición hecha
        # hacemos lo mismo que en los recursos anteriores, de analizar esos resultados.
        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            limit = 10 #Ponemos limit 10 por defecto

            drug=self.path.split('=')[1]
            drugs = []
            conn = http.client.HTTPSConnection(self.API_URL)
            conn.request("GET", self.API_PETICION + "?limit="+str(limit) + self.API_DRUG + drug)
            r1 = conn.getresponse()
            fichero_raw = r1.read().decode("utf8")
            fichero = json.loads(fichero_raw)
            resultados = fichero['results']

            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    drugs.append(resultado['openfda']['generic_name'][0])
                else:
                    drugs.append('Desconocido')

            searchDrug_html = self.recurso_web(drugs)
            self.wfile.write(bytes(searchDrug_html, "utf8"))

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            limit = 10

            company=self.path.split('=')[1]
            companies = []
            conn = http.client.HTTPSConnection(self.API_URL)
            conn.request("GET", self.API_PETICION + "?limit=" + str(limit) + self.API_COMPANY + company)
            r1 = conn.getresponse()
            fichero_raw = r1.read().decode("utf8")
            fichero = json.loads(fichero_raw)
            resultados = fichero['results']

            for resultado in resultados:
                companies.append(resultado['openfda']['manufacturer_name'][0])
            searchCompany_html = self.recurso_web(companies)
            self.wfile.write(bytes(searchCompany_html, "utf8"))

        #Extensiones
        elif 'secret' in self.path:# Autenticación obligatoria
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()
        elif 'redirect' in self.path:#Si pones el recurso /redirect te llevara a la pággina de los formularios
            self.send_response(302)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()
        else:
            self.send_response(404) #Por si pones un recurso que no exista
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Este recurso no existe".format(self.path).encode())
        return

#EMPIEZA EL SERVIDOR
#Nos permite siempre utilizar el mismo puerto
socketserver.TCPServer.allow_reuse_address= True
#Configurar el socket del servidor, para esperar conexiones de clientes
#Instancia de una clase, responde peticiones http (manejador)
Handler = testHTTPRequestHandler
#Asocia una ip y un puerto al manejador de peticiones
httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en el puerto:", PORT)
httpd.serve_forever()#Servidor siempre activo