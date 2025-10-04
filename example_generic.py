from web import Server, Page
import sys
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
    
page = Page()
page.add_action_component('Change Light', led.toggle)
page.add_on_off_component('LED integrado:', led.on, led.off)
page.add_range_value_component('Blink times : ', 1, 10, 1, multiblink)
page.add_range_value_component('Time of blink: ', 0, 1000, 500, blink_time)

Server("Hachiko_24", "iquique47", page)
