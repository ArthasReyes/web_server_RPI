from web import Server, Page
import sys
from time import sleep_ms
from machine import Pin, PWM

led = Pin("LED", Pin.OUT)

page = Page()
page.add_action_component('Change Light', multiblink)
page.add_on_off_component('LED integrado:', led.on, led.off)
page.add_range_value_component('Freq is: ', 0, 1000, 500, multiblinktime)
page.add_range_value_component('Freq is: ', 1, 10, 500, multiblinktime2)

Server("Hachiko_24", "iquique47", page)
