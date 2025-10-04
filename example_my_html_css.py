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
  for _ in range(times):
    led.toggle()
    sleep_ms(time)

with open("style.css", "r") as f:
    my_css = f.read()

with open("style.css", "r") as f:
    my_html = f.read()

#Conecto las acciones a los componentes
page = Page(html = my_html, css= my_css)
page.add_action_component("EncenderLED", led.on)
page.add_action_component("ApagarLED", led.off)
Server("Hachiko_24", "iquique47", page)
