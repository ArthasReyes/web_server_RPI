from web import Server, Page, Wifi
from asyncio import sleep, sleep_ms, run
from machine import Pin, PWM

led = Pin("LED", Pin.OUT)

with open("style.css", "r") as f:
    my_css = f.read()

with open("site.html", "r") as f:
    my_html = f.read()

page = Page(html = my_html, css= my_css)
page.add_action_component("EncenderLED", led.on)
page.add_action_component("ApagarLED", led.off)

async def main():
    Wifi("Hachiko_24", "iquique47")
    server = Server(page)
    await server.start_server()

if __name__ == "__main__":
    run(main())
