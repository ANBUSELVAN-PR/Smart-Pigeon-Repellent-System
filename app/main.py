from pathlib import Path
from fastapi import FastAPI, Depends, Header, HTTPException, UploadFile, File, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from PIL import Image
from app.core.config import settings
from app.db.session import Base, engine, get_db
from app.models import Device, DetectionEvent, RepellentEvent
from app.schemas.api import SensorEventIn, DetectionOut, ConfigOut, RepellentStatusIn
from app.services.inference.service import infer

app = FastAPI(title="Smart Pigeon Repellent API", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(engine)
def auth(x_device_token: str | None = Header(default=None)):
    if x_device_token != settings.device_token: raise HTTPException(status_code=401, detail="Invalid device token")
@app.get("/health")
def health(): return {"status":"ok", "inference_provider":settings.inference_provider}
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request): return templates.TemplateResponse("dashboard.html", {"request": request})
@app.post("/api/devices/events", dependencies=[Depends(auth)])
def sensor_event(data: SensorEventIn, db: Session = Depends(get_db)):
    d = db.query(Device).filter_by(device_id=data.device_id).first() or Device(device_id=data.device_id, device_type="esp32")
    d.last_seen = __import__('datetime').datetime.now(__import__('datetime').timezone.utc); d.status = "online"; db.add(d)
    event = DetectionEvent(device_id=data.device_id, detected=False, capture_status="capture_requested" if data.motion and data.distance_cm is not None and data.distance_cm <= settings.detection_distance_cm else "rejected", sensor_readings={**data.readings, "motion":data.motion, "distance_cm":data.distance_cm})
    db.add(event); db.commit(); db.refresh(event); return {"event_id":event.id, "capture_request": {"required": event.capture_status=="capture_requested", "event_id":event.id} if event.capture_status=="capture_requested" else None}
@app.get("/api/devices/capture-request/{event_id}", dependencies=[Depends(auth)])
def capture_request(event_id: int, db: Session=Depends(get_db)):
    event=db.get(DetectionEvent,event_id)
    if not event: raise HTTPException(404,"Sensor event not found")
    return {"event_id":event.id,"required":event.capture_status=="capture_requested","status":event.capture_status}
@app.post("/api/detections/image", response_model=DetectionOut, dependencies=[Depends(auth)])
async def image_upload(device_id: str, event_id: int, image: UploadFile = File(...), db: Session = Depends(get_db)):
    if not __import__('re').fullmatch(r"[A-Za-z0-9_-]{1,80}", device_id): raise HTTPException(422,"Invalid device id")
    if image.content_type not in {"image/jpeg", "image/png"}: raise HTTPException(415, "JPEG or PNG required")
    content = await image.read(settings.max_image_bytes + 1)
    if len(content) > settings.max_image_bytes: raise HTTPException(413, "Image too large")
    event=db.get(DetectionEvent,event_id)
    if not event or event.device_id != device_id: raise HTTPException(404,"Sensor event not found")
    path = Path(settings.upload_dir).resolve() / f"{device_id}_{__import__('time').time_ns()}.jpg"
    try:
        import io
        with Image.open(io.BytesIO(content)) as im: im.verify()
    except Exception as e: raise HTTPException(400, "Invalid image") from e
    path.write_bytes(content); prediction = infer(path)
    event.detected=prediction.detected and (prediction.confidence or 0) >= settings.confidence_threshold; event.detection_class=prediction.label; event.confidence=prediction.confidence; event.image_path=str(path); event.capture_status="inference_complete"
    if event.detected:
        event.repellent_events.append(RepellentEvent(outcome="commanded"))
    db.commit(); db.refresh(event); return event
@app.post("/api/repellent/command", dependencies=[Depends(auth)])
def repellent_command(detection_id: int, db: Session=Depends(get_db)):
    detection=db.get(DetectionEvent,detection_id)
    if not detection or not detection.detected: raise HTTPException(409,"Repellent requires confirmed pigeon detection")
    item=RepellentEvent(detection_id=detection_id,outcome="commanded"); db.add(item); db.commit(); db.refresh(item)
    return {"repellent_id":item.id,"command":"activate","max_duration_s":settings.max_repellent_duration_s}
@app.get("/api/devices/{device_id}/commands", dependencies=[Depends(auth)])
def device_commands(device_id: str, db: Session=Depends(get_db)):
    if not __import__('re').fullmatch(r"[A-Za-z0-9_-]{1,80}", device_id): raise HTTPException(422,"Invalid device id")
    item=(db.query(RepellentEvent).join(DetectionEvent).filter(DetectionEvent.device_id==device_id, RepellentEvent.outcome=="commanded", RepellentEvent.command_claimed_at.is_(None)).order_by(RepellentEvent.activation_time).first())
    if not item: return {"command":None}
    item.command_claimed_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc); db.commit()
    return {"command":"activate","repellent_id":item.id,"detection_id":item.detection_id,"max_duration_s":settings.max_repellent_duration_s,"frequency_min_hz":settings.buzzer_min_hz,"frequency_max_hz":settings.buzzer_max_hz,"change_interval_s":settings.frequency_change_interval_s}
@app.post("/api/repellent/status", dependencies=[Depends(auth)])
def repellent_status(data: RepellentStatusIn, db: Session=Depends(get_db)):
    item=db.get(RepellentEvent,data.repellent_id)
    if not item: raise HTTPException(404,"Repellent event not found")
    item.outcome=data.status; item.duration_s=max(item.duration_s,data.duration_s)
    frequencies=list(item.frequencies or [])
    if data.frequency_hz and data.frequency_hz not in frequencies: frequencies.append(data.frequency_hz)
    item.frequencies=frequencies
    if data.status in {"completed","stopped","timeout","communication_failed"}: item.completed_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc)
    device=db.query(Device).filter_by(device_id=data.device_id).first()
    if device: device.last_seen=__import__('datetime').datetime.now(__import__('datetime').timezone.utc); device.status="online"
    db.commit(); return {"repellent_id":item.id,"recorded":True}
@app.get("/api/detections", response_model=list[DetectionOut])
def detections(db: Session = Depends(get_db)): return db.query(DetectionEvent).order_by(DetectionEvent.timestamp.desc()).limit(100).all()
@app.get("/api/config", response_model=ConfigOut)
def config(): return ConfigOut(detection_distance_cm=settings.detection_distance_cm, confidence_threshold=settings.confidence_threshold, buzzer_min_hz=settings.buzzer_min_hz, buzzer_max_hz=settings.buzzer_max_hz, cooldown_s=settings.cooldown_s)
@app.get("/api/summary")
def summary(db: Session = Depends(get_db)):
    return {"confirmed_detections": db.query(DetectionEvent).filter_by(detected=True).count(), "sensor_events": db.query(DetectionEvent).count(), "repellent_activations": db.query(RepellentEvent).count(), "inference_provider":settings.inference_provider}
@app.get("/api/repellents")
def repellents(db: Session=Depends(get_db)): return db.query(RepellentEvent).order_by(RepellentEvent.activation_time.desc()).limit(100).all()
@app.get("/api/devices")
def devices(db: Session=Depends(get_db)): return db.query(Device).order_by(Device.last_seen.desc()).all()
@app.get("/api/analytics")
def analytics(db: Session=Depends(get_db)):
    from collections import Counter
    rows=db.query(DetectionEvent).all()
    daily=Counter(x.timestamp.date().isoformat() for x in rows if x.detected)
    weekly=Counter(x.timestamp.isocalendar().week for x in rows if x.detected)
    return {"daily_detections":dict(sorted(daily.items())),"weekly_detections":{str(k):v for k,v in sorted(weekly.items())}}
