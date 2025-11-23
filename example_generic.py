from web import Server, Page, Wifi
from asyncio import sleep, sleep_ms, run
from machine import Pin, PWM

led = Pin("LED", Pin.OUT)
    
async def multiblink(times):
    for _ in range(times*2):
        led.toggle()
        await sleep(0.5)
        
page = Page()
page.add_action_component("Luces", led.toggle)
page.add_on_off_component("Luces", led.on, led.off)
page.add_range_value_component("Multiblink", 1, 10, 5, multiblink)


async def main():
    Wifi("Hachiko_24", "iquique47")
    server = Server(page)
    await server.start_server()

if __name__ == "__main__":
    run(main())
