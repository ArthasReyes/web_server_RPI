from machine import Pin, PWM
from asyncio import sleep

class Buzzer:
    def __init__(self, pin: int) -> None:
        self.pin = Pin(pin)
        self.buzzer = PWM(self.pin)
        
        self.octava = {
            "Do": 261,
            "Re": 293,
            "Mi": 329,
            "Fa": 349,
            "Sol": 391,
            "La": 440,
            "Si": 493,
            "Dom": 523,
            "Rem": 587,
            "Mim": 659,
            "Fam": 698,
        }
        self.nota_mus= {
            "redonda": 1,
            "blanca": 1/2,
            "negra": 1/4,
            "corchea": 1/8,
            "semicorchea": 1/16
        }
    
    def on(self, frecuencia: int=440) -> None:
        self.buzzer.freq(frecuencia)
        self.buzzer.duty_u16(2**15)
        
    def off(self) -> None:
        self.buzzer.duty_u16(0)
        
    async def tone(self, frecuencia: int, duracion: float, silencio: float = 0) -> None:
        self.on(frecuencia)
        await sleep(duracion)
        self.off()
        await sleep(silencio)
        
    async def play_song(self, song):
        for note in song:
            await self.tone(self.octava[note[0]],self.nota_mus[note[1]],note[2])
