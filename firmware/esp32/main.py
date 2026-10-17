try:
    from config import *
    from sensors import Sensors
    from repellent import Repellent
    from http_client import post_sensor, poll_command, post_status
except ImportError:
    from .config import *
    from .sensors import Sensors
    from .repellent import Repellent
    from .http_client import post_sensor, poll_command, post_status
import time
def main():
    s=Sensors(PIR_PIN,TRIG_PIN,ECHO_PIN); b=Repellent(BUZZER_PIN,1800,4200,8,MAX_REPELLENT_SECONDS)
    while True:
        if s.motion() and (d:=s.distance_cm()) is not None:
            response=post_sensor({"device_id":DEVICE_ID,"motion":True,"distance_cm":d})
            # Sensor confirmation requests a capture only; inference must command repellent.
            if response.get("capture_request"): pass
        command=poll_command(DEVICE_ID)
        if command and command.get("command")=="activate":
            b.activate(command, lambda status,duration,freq: post_status(DEVICE_ID,command["repellent_id"],status,duration,freq))
        b.stop(); time.sleep(.2)
if __name__=="__main__": main()
