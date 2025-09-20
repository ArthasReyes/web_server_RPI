from web import Server, Page
from time import sleep_ms
from machine import Pin, PWM

led = Pin("LED", Pin.OUT)
def blink_time(time):
  led.toggle()
  sleep_ms(time)
  led.toggle()
  sleep_ms(time)

def multiblink(times):
  for i in range(times):
    led.toggle()
    sleep_ms(time)

my_css = """
body { font-family: Arial; background: #fafafa; }
    h1 { color: navy; }
    form { margin: 10px; }
    input[type="submit"] { background: blue; color: white; padding: 10px; }
    """

my_html = """
<!DOCTYPE html>
<html>
<head>
  <style></style>
</head>
<body>
  <h1>Control de LEDs</h1>
  <form action="./EncenderLED"><input type="submit" value="Encender LED"></form>
  <form action="./ApagarLED"><input type="submit" value="Apagar LED"></form>
</body>
</html>

"""

#Conecto las acciones a los componentes
page = Page(html = my_html, css= my_css)
page.add_action_component("EncenderLED", led.on)
page.add_action_component("ApagarLED", led.off)
Server("Hachiko_24", "iquique47", page)