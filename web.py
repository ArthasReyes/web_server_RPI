import network
import socket
from time import sleep

class Server:
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
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #connection = socket.socket()
        connection.bind(address)
        connection.listen(1)
        return connection
        

    def serve(self, connection):
        #Start a web server
        while True:
            client = connection.accept()[0]
            request = str(client.recv(1024))
            if len(request.split()) > 1: # Check if there's a second element before accessing
                request_path = request.split()[1]
                print(request_path)
                argument = self.get_argument(request_path) if self.has_argument(request_path) else None
                action_name = self.get_action_query(request_path)
                print(f"Action Name: {action_name}", f"Arguments: {argument}")
                action = self.web_page.actions.get(action_name, self.web_page.print_error_name)
                
                if argument is None:
                    action()
                else:
                    action(argument)
                html = self.web_page.render()
                client.send(html)
            else:
                print("Invalid request format") # Handle cases where request is not as expected
                html = self.web_page.render() # Still render page even on invalid request?
                client.send(html)
            client.close()
    def has_argument(self, path):
        if path.find("=") > 1:
           return True
        return False
    
    def get_argument(self, path):
        inicio_palabra = path.find('=')+1
        if inicio_palabra == 0:
            return None
        return path[inicio_palabra:]
        
    def get_action_query(self, path):
        inicio_palabra = path.find('/') # Encuentra la posición de la barra inicial
        if inicio_palabra == -1: # Si no se encuentra '/', la ruta no es válida
            return None

        inicio_palabra += 1 # Ajusta el inicio para que esté después de la barra

        fin_palabra = path.find('?', inicio_palabra) # Busca '?' desde el inicio de la palabra
        if fin_palabra == -1: # Si no se encuentra '?', la palabra llega hasta el final de la ruta
            return path[inicio_palabra:]
        else:
            return path[inicio_palabra:fin_palabra] # Extrae la palabra entre '/' y '?'

css_default = """
    
            body {
                font-family: Ubuntu, Arial, sans-serif;
                background-color: #f0f0f0;
                height: 100vh;
                margin: 0;
            }
            
            form {
            margin: 10px;
            display: flex; 
            align-items: center;  
            }

            form > * {
                margin-right: 10px; 
                margin-bottom: 5px; 
                display: inline-block; 
                vertical-align: middle; 
            }
                    
            input {
                padding: 10px 20px;
                margin: 5px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }

            input:hover {
                background-color: #4CAF50;
                color: white;
            }

            input:focus {
                outline: none;
            }
            
            input[type="checkbox"] {
                appearance: none;
                -webkit-appearance: none;
                width: 60px;
                height: 30px;
                background-color: #ccc;
                border-radius: 15px;
                position: relative;
                cursor: pointer;
                transition: background-color 0.3s;
                margin: 10px 0;
            }

            input[type="checkbox"]::before {
                content: "";
                position: absolute;
                top: 2px;
                left: 2px;
                width: 26px;
                height: 26px;
                border-radius: 50%;
                background-color: white;
                transition: left 0.3s;
            }

            input[type="checkbox"]:checked {
                background-color: #4CAF50;
            }

            input[type="checkbox"]:checked::before {
                left: 32px;
            }
        
        """
class Page:
    def __init__(self, css = None):
        if css is None:
            css = css_default
        self.css = css
        self.placeholder = "<input type='hidden'><br>"
        self.actions = {"":self.print_welcome_page}
        self.components = []
        self.new_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <link rel="icon" href="data:,">
                <style>{self.css}</style>
                </head>
                <body>
                {self.placeholder}
                </body>
                </html>
                """
        self.content = self.new_content
    def print_welcome_page(self):
        print("Bienvenido ", self.actions.keys())
        
    def print_error_name(self):
        print("Accion no válida, las acciones validas son: ", self.actions.keys())
        
    def add_action_component(self, label, func):
        component = Action_component(self, label, func)
        self.components.append(component)    
    
    def add_on_off_component(self, label, func_on, func_off):
        component = On_off_component(self, label, func_on, func_off)
        self.components.append(component)
    
    def add_range_value_component(self, label, minimum, maximum, started, func_on_change):
        component = Range_value_component(self, label, minimum, maximum, started, func_on_change)
        self.components.append(component)
        
    def add_content(self, formated_content):
        self.content = self.content.replace(self.placeholder, formated_content+self.placeholder)
                
    def render(self):
        self.content = self.new_content 
        for component in self.components:
            component.render()
        return str(self.content)


class Component:
    def __init__(self, page, label):
        self.page = page
        self.label = label
        
    def label_to_action(self, label):
        action = ''
        for char in label:
            if ('0' <= char <= '9') or ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
                action += char
        return action
    
    def add_action(self, action, func):
        self.page.actions[f'{action}'] = func
        
class Action_component(Component):
    def __init__(self, page, label, func):
        super().__init__(page, label)

        self.action = self.label_to_action(self.label)
        self.add_action(self.action, func)
        
    def render(self):
        formated_content = f"<form action='./{self.action}'><input type='submit' value='{self.label}' /></form>"
        self.page.add_content(formated_content)        
    

class On_off_component(Component):
    def __init__(self, page, label, func_on, func_off):
        super().__init__(page, label)

        self.action_on = self.label_to_action(self.label)+"ON"
        self.action_off = self.label_to_action(self.label)+"OFF"
        self.func_on = func_on
        self.func_off = func_off
        self.add_action(self.action_on, self.change_state)
        self.add_action(self.action_off, self.change_state)
        self.state = False
    
    def change_state(self, arg=None):
        if arg == "on":
            self.func_on()
            self.state = False
        else:
            self.func_off()
            self.state = True
        
    def render(self):
        state_checked = 'checked' if not self.state else ''
        state_action = str(self.action_on) if self.state else str(self.action_off)
        name_comp = state_action
        id_comp =  state_action
        formated_content = f"<form action='./{state_action}' ><label id='{id_comp}'>{self.label}</label><input onchange='this.form.submit()' type='checkbox' { state_checked } name='{name_comp}' id='{id_comp}'></form>"
        self.page.add_content(formated_content)
        
class Range_value_component(Component):
    def __init__(self, page, label, minimum, maximum, started_value, onchange_func):
        super().__init__(page, label)
        self.onchange_action = self.label_to_action(self.label)+"RANGE"
        self.name_comp = self.onchange_action
        self.id_comp =  self.onchange_action
        self.onchange_func = onchange_func
        self.add_action(self.onchange_action, self.onchange_state) 
        self.started_value = started_value
        self.minimum_value = minimum
        self.maximum_value = maximum
    
    def onchange_state(self, args):
        self.started_value = int(args)
        self.onchange_func(self.started_value)

    def render(self):
        formated_content = f"<form action='./{self.onchange_action}' ><label id='{self.id_comp}'>{self.label}</label><input onchange='this.form.submit()' type='range' id='{self.id_comp}' name='{self.name_comp}' min='{self.minimum_value}' max='{self.maximum_value}' value='{self.started_value}'></form>"
        self.page.add_content(formated_content)
