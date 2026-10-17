import random,time
from machine import PWM,Pin
class Repellent:
    def __init__(self,pin,low,high,interval,maximum): self.pwm=PWM(Pin(pin),freq=low,duty=0); self.low=low; self.high=high; self.interval=interval; self.maximum=maximum
    def run(self, pigeon_present=True):
        started=time.time(); previous=None
        while pigeon_present and time.time()-started<self.maximum:
            choices=[x for x in range(self.low,self.high+1,100) if x!=previous] or [self.low]; previous=random.choice(choices); self.pwm.freq(previous); self.pwm.duty(512); yield previous; time.sleep(self.interval)
        self.stop()
    def stop(self): self.pwm.duty(0)
    def activate(self, command, report):
        started=time.time(); previous=None; report("started",0,None)
        while time.time()-started < min(self.maximum, command.get("max_duration_s",self.maximum)):
            choices=[x for x in range(command.get("frequency_min_hz",self.low),command.get("frequency_max_hz",self.high)+1,100) if x!=previous] or [self.low]
            previous=random.choice(choices); self.pwm.freq(previous); self.pwm.duty(512); report("frequency_changed",int(time.time()-started),previous); time.sleep(command.get("change_interval_s",self.interval))
        self.stop(); report("completed",int(time.time()-started),None)
