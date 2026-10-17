import ujson, urequests
try: from config import SERVER_URL, DEVICE_TOKEN
except ImportError: from .config import SERVER_URL, DEVICE_TOKEN
def post_sensor(payload):
    r=urequests.post(SERVER_URL+"/api/devices/events",headers={"X-Device-Token":DEVICE_TOKEN,"Content-Type":"application/json"},data=ujson.dumps(payload)); out=r.json(); r.close(); return out
def post_status(device_id,repellent_id,status,duration_s=0,frequency_hz=None):
    payload={"device_id":device_id,"repellent_id":repellent_id,"status":status,"duration_s":duration_s,"frequency_hz":frequency_hz}
    r=urequests.post(SERVER_URL+"/api/repellent/status",headers={"X-Device-Token":DEVICE_TOKEN,"Content-Type":"application/json"},data=ujson.dumps(payload)); out=r.json(); r.close(); return out
def poll_command(device_id):
    r=urequests.get(SERVER_URL+"/api/devices/"+device_id+"/commands",headers={"X-Device-Token":DEVICE_TOKEN}); out=r.json(); r.close(); return out.get("command")
