import uasyncio as asyncio
import socket
import network
from time import sleep

class Server:
    def __init__(self, web_page):
        self.web_page = web_page
        
    
    async def start_server(self):
        print("Starting server...")
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
        else:
            ip = "0.0.0.0"
            
        print(f"Binding to {ip}:80")
        self.server = await asyncio.start_server(self.handle_client, ip, 80)
        print("Server started.")
        while True:
            await asyncio.sleep(3600)

    async def handle_client(self, reader, writer):
        try:
            print("Client connected")
            request_line = await reader.readline()
            if not request_line:
                print("Client disconnected or empty request")
                return
            
            request = request_line.decode("utf-8").strip()
            print(f"Request: {request}")
            parts = request.split()

            if len(parts) < 2:
                return

            method = parts[0]
            request_path = parts[1]
            
            while True:
                header = await reader.readline()
                if not header or header == b'\r\n' or header == b'\n':
                    break

            if request_path == "/favicon.ico":
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            argument = self.get_argument(request_path) if self.has_argument(request_path) else None
            action_name = self.get_action_query(request_path)
            
            print(f"Action Name: {action_name}", f"Arguments: {argument}")

            if action_name and action_name in self.web_page.actions:
                action = self.web_page.actions[action_name]
                
                try:
                    if argument is None:
                        result = action()
                    else:
                        result = action(argument)
                    
                    if hasattr(result, "send"): 
                        print(f"Scheduling async task: {action_name}")
                        asyncio.create_task(result)
                except Exception as e:
                    print(f"Error executing action {action_name}: {e}")
                
                writer.write(b"HTTP/1.1 204 No Content\r\n")
                writer.write(b"Access-Control-Allow-Origin: *\r\n\r\n")
            else:
                html = self.web_page.render()
                writer.write(b"HTTP/1.1 200 OK\r\n")
                writer.write(b"Content-Type: text/html\r\n")
                writer.write(b"Connection: close\r\n\r\n")
                writer.write(html.encode('utf-8'))

            await writer.drain()
        except Exception as e:
            print("Error in handle_client:", e)
        finally:
            writer.close()
            await writer.wait_closed()
            
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
        inicio_palabra = path.find('/') 
        if inicio_palabra == -1:
            return None

        inicio_palabra += 1 

        fin_palabra = path.find('?', inicio_palabra) 
        if fin_palabra == -1:
            return path[inicio_palabra:]
        else:
            return path[inicio_palabra:fin_palabra] 

css_default = """
    
            body {
                font-family: Ubuntu, Arial, sans-serif;
                background-color: #f0f0f0;
                height: 100vh;
                margin: 0;
            }
            
            .control-container {
            margin: 10px;
            display: flex; 
            align-items: center;  
            }

            .control-container > * {
                margin-right: 10px; 
                margin-bottom: 5px; 
                display: inline-block; 
                vertical-align: middle; 
            }
                    
            button, input[type="submit"] {
                padding: 10px 20px;
                margin: 5px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
                background-color: #ddd;
                border: 1px solid #ccc;
            }

            button:hover, input[type="submit"]:hover {
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

html_default = """
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style></style>
                <script>
                function sendAction(url) {
                    fetch(url, { method: 'GET' })
                        .then(response => {
                            if (response.ok) {
                                console.log("Action executed: " + url);
                            } else {
                                console.error("Error executing action");
                            }
                        })
                        .catch(error => console.error('Error:', error));
                }
                </script>
                </head>
                <body>
                <input type='hidden'><br>
                </body>
                </html>
                """

class Page:
    def __init__(self, html=None, css = None):
        if css is None:
            css = css_default
        self.css = css
        
        if html is None:
            html = html_default
        self.html = html
        
        self.placeholder = "<input type='hidden'><br>"
        self.actions = {"":self.print_welcome_page}
        self.components = []
        
        self.new_content = self.html.replace("<style></style>", "<style>"+self.css+"</style>")
        
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
        formated_content = f"<div class='control-container'><button onclick=\"sendAction('./{self.action}')\">{self.label}</button></div>"
        self.page.add_content(formated_content)        
    

class On_off_component(Component):
    def __init__(self, page, label, func_on, func_off):
        super().__init__(page, label)

        self.action_on = self.label_to_action(self.label)+"ON"
        self.action_off = self.label_to_action(self.label)+"OFF"
        self.func_on = func_on
        self.func_off = func_off

        self.add_action(self.action_on, self.do_on)
        self.add_action(self.action_off, self.do_off)
        self.state = False
        
    def do_on(self, arg=None):
        print(f"Turning ON {self.label}")
        result = self.func_on()
        self.state = False
        return result

    def do_off(self, arg=None):
        print(f"Turning OFF {self.label}")
        result = self.func_off()
        self.state = True
        return result
        
    def render(self):
        state_checked = 'checked' if not self.state else ''
        
        action_on = self.action_on
        action_off = self.action_off
        
        id_comp = self.label_to_action(self.label)

        script = f"sendAction(this.checked ? './{action_on}' : './{action_off}')"
        
        formated_content = f"<div class='control-container'><label for='{id_comp}'>{self.label}</label><input type='checkbox' id='{id_comp}' {state_checked} onchange=\"{script}\"></div>"
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
        return self.onchange_func(self.started_value)

    def render(self):
        script = f"sendAction('./{self.onchange_action}?val=' + this.value)"
        
        formated_content = f"<div class='control-container'><label for='{self.id_comp}'>{self.label}</label><input type='range' id='{self.id_comp}' min='{self.minimum_value}' max='{self.maximum_value}' value='{self.started_value}' onchange=\"{script}\"></div>"
        self.page.add_content(formated_content)


class Wifi:
    def __init__(self, ssid, password):
        #Connect to WLAN
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('Waiting for connection...')
            sleep(1)
        self.ip = wlan.ifconfig()[0]
        print(f"connected to {self.ip}")
        


