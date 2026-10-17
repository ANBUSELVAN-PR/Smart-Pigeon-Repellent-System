import time
from machine import Pin, time_pulse_us
class Sensors:
    def __init__(self,pir_pin,trig_pin,echo_pin): self.pir=Pin(pir_pin,Pin.IN); self.trig=Pin(trig_pin,Pin.OUT); self.echo=Pin(echo_pin,Pin.IN)
    def distance_cm(self):
        self.trig.value(0); time.sleep_us(2); self.trig.value(1); time.sleep_us(10); self.trig.value(0); p=time_pulse_us(self.echo,1,30000); return None if p<0 else p/58
    def motion(self): return bool(self.pir.value())
