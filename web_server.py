import network
import socket
from time import sleep
from machine import Pin


class Web_server:
    def __init__(self, ssid, password, web_page):
        self.web_page = web_page
        ip = self.connect(ssid, password)
        connection = self.open_socket(ip)
        self.serve(connection)
    
    
    def connect(self, ssid, password):
        #Connect to WLAN
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('Waiting for connection...')
            sleep(1)
        ip = wlan.ifconfig()[0]
        print(f"connected to {ip}")
        return ip

    def open_socket(self, ip):
        # Open a socket
        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(1)
        print(f"connection at {connection}")
        return connection
        

    def serve(self, connection):
        #Start a web server
        while True:
            client = connection.accept()[0]
            request = str(client.recv(1024))
            request = request.split()[1]
            print(request)
            action = self.web_page.actions.get(request, self.web_page.print_error_name)()
            html = self.web_page.render()
            client.send(html)
            client.close()

class Web_page:
    def __init__(self):
        self.actions = {}
        self.page = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <link rel="icon" href="data:,">
                </head>
                <body>
                <<elements>>
                </body>
                </html>
                """
        def print_error_name(self):
            print("Accion no válida")
            
        def add_button(self, action, func, value):
            self.page = self.page.replace("<<elements>>", f"<form action='./{action}'><input type='submit' value='{value}' /></form> <<elements>>")
            self.actions.append({f'/{action}?': func})
              
        
        def render(self):
            return str(self.page)