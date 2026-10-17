from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
client=TestClient(app)
def test_health():
    assert client.get('/health').status_code==200
def test_auth():
    assert client.post('/api/devices/events',json={'device_id':'x','motion':False},headers={'X-Device-Token':'bad'}).status_code==401
def test_event():
    r=client.post('/api/devices/events',json={'device_id':'test','motion':True,'distance_cm':20},headers={'X-Device-Token':settings.device_token}); assert r.status_code==200; assert r.json()['capture_request']['required'] is True
def test_invalid_device_id():
    r=client.post('/api/devices/events',json={'device_id':'bad/id','motion':False},headers={'X-Device-Token':settings.device_token}); assert r.status_code==422
def test_mock_inference(tmp_path):
    from app.services.inference.service import infer
    assert infer(tmp_path/'missing.jpg').provider=='mock-simulated'
def test_capture_does_not_activate_buzzer():
    r=client.post('/api/devices/events',json={'device_id':'sensor_only','motion':True,'distance_cm':10},headers={'X-Device-Token':settings.device_token})
    assert r.json()['capture_request']['required'] is True
    assert client.get('/api/devices/sensor_only/commands',headers={'X-Device-Token':settings.device_token}).json()['command'] is None
def test_invalid_image_rejected():
    e=client.post('/api/devices/events',json={'device_id':'image_test','motion':True,'distance_cm':10},headers={'X-Device-Token':settings.device_token}).json()['event_id']
    r=client.post('/api/detections/image',params={'device_id':'image_test','event_id':e},files={'image':('x.jpg',b'not-an-image','image/jpeg')},headers={'X-Device-Token':settings.device_token})
    assert r.status_code==400
def test_confirmed_detection_creates_command(monkeypatch):
    from app.services.inference.base import Prediction
    import app.main as main
    monkeypatch.setattr(main,'infer',lambda path: Prediction(True,'pigeon',.91,'test'))
    e=client.post('/api/devices/events',json={'device_id':'confirmed','motion':True,'distance_cm':10},headers={'X-Device-Token':settings.device_token}).json()['event_id']
    from PIL import Image
    import io
    buf=io.BytesIO(); Image.new('RGB',(2,2),'white').save(buf,format='JPEG')
    r=client.post('/api/detections/image',params={'device_id':'confirmed','event_id':e},files={'image':('x.jpg',buf.getvalue(),'image/jpeg')},headers={'X-Device-Token':settings.device_token})
    assert r.status_code==200 and r.json()['detected'] is True
    command=client.get('/api/devices/confirmed/commands',headers={'X-Device-Token':settings.device_token}).json()
    assert command['command']=='activate'
    status=client.post('/api/repellent/status',json={'device_id':'confirmed','repellent_id':command['repellent_id'],'status':'completed','duration_s':4,'frequency_hz':2200},headers={'X-Device-Token':settings.device_token})
    assert status.status_code==200
