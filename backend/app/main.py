import json, secrets, hashlib, csv, io
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import Base, engine, get_db
from app.models import User, Analysis, Device, TestSession, SensorReading
from app.schemas import AuthIn, AnalyzeIn, DeviceIn, SessionIn, IngestIn
from app.auth import hash_password, verify_password, make_token, current_user
from app.config import CORS_ORIGINS, DEVICE_API_KEY
from app.ml.model import predict, model_info
from app.ml.profiles import PROFILES

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart FoodGuard AI API", version="1.0.0",
 description="Student demo API. Synthetic model outputs are not validated food tests.")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def analysis_dict(a):
    return {"id":a.id,"sample_id":a.sample_id,"food":a.food,"mode":a.mode,"result":a.result,
      "model_output":a.model_output,"measurements":json.loads(a.measurements_json),"created_at":a.created_at.isoformat() if a.created_at else None}

@app.get("/api/health")
def health(): return {"status":"ok","service":"Smart FoodGuard AI API","time":datetime.now(timezone.utc).isoformat()}

@app.post("/api/auth/signup")
def signup(data: AuthIn, db: Session=Depends(get_db)):
    email=data.email.lower().strip()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(409,"Email already registered")
    user=User(email=email,password_hash=hash_password(data.password)); db.add(user); db.commit(); db.refresh(user)
    return {"access_token":make_token(user.id),"token_type":"bearer","email":user.email}

@app.post("/api/auth/login")
def login(data: AuthIn, db: Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email.lower().strip()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":make_token(user.id),"token_type":"bearer","email":user.email}

@app.get("/api/auth/me")
def me(user: User=Depends(current_user)): return {"id":user.id,"email":user.email}

@app.get("/api/foods")
def foods():
    return [{"id":k,"name":k.title(),"features":v["features"],"units":v["units"],"profile_note":"Example placeholder profile; not scientifically validated"} for k,v in PROFILES.items()]

@app.post("/api/analyze")
def analyze(data: AnalyzeIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    if data.food not in PROFILES: raise HTTPException(422,"Unsupported food category")
    if data.mode not in ("manual","demo","hardware"): raise HTTPException(422,"Mode must be manual, demo, or hardware")
    if not data.measurements: raise HTTPException(422,"At least one measurement is required")
    if any(not isinstance(v,(int,float)) or not (-1e9 < float(v) < 1e9) for v in data.measurements.values()):
        raise HTTPException(422,"Measurements must be finite numeric values")
    output=predict(data.food,data.measurements)
    label = "Manually Entered Data" if data.mode=="manual" else ("SIMULATED DEMONSTRATION" if data.mode=="demo" else "Hardware readings")
    record=Analysis(user_id=user.id,sample_id=data.sample_id,food=data.food,mode=data.mode,result=output["result"],
      model_output=output["model_output"],measurements_json=json.dumps(data.measurements))
    db.add(record); db.commit(); db.refresh(record)
    result=analysis_dict(record); result.update({"source_label":label,"model":output,"disclaimer":"This is a preliminary screening demonstration, not a certified food safety test. Results depend on the quality of the reference dataset, sensor accuracy, and model validation. A normal result does not establish that food is safe, and an unusual result does not prove adulteration. Use an appropriate validated laboratory test for confirmation."})
    return result

@app.get("/api/history")
def history(db: Session=Depends(get_db), user: User=Depends(current_user)):
    return [analysis_dict(a) for a in db.query(Analysis).filter(Analysis.user_id==user.id).order_by(Analysis.id.desc()).all()]

@app.get("/api/history/{analysis_id}")
def history_one(analysis_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    a=db.query(Analysis).filter(Analysis.id==analysis_id,Analysis.user_id==user.id).first()
    if not a: raise HTTPException(404,"Analysis not found")
    return analysis_dict(a)

@app.delete("/api/history/{analysis_id}")
def history_delete(analysis_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    a=db.query(Analysis).filter(Analysis.id==analysis_id,Analysis.user_id==user.id).first()
    if not a: raise HTTPException(404,"Analysis not found")
    db.delete(a); db.commit(); return {"deleted":True}

@app.get("/api/history/export.csv")
def export_csv(db:Session=Depends(get_db), user:User=Depends(current_user)):
    records=db.query(Analysis).filter(Analysis.user_id==user.id).order_by(Analysis.id.desc()).all()
    out=io.StringIO(); writer=csv.writer(out); writer.writerow(["id","sample_id","food","mode","result","created_at","measurements"])
    for a in records: writer.writerow([a.id,a.sample_id,a.food,a.mode,a.result,a.created_at,json.dumps(json.loads(a.measurements_json))])
    return Response(out.getvalue(),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=foodguard-history.csv"})

@app.get("/api/dashboard/stats")
def stats(db:Session=Depends(get_db), user:User=Depends(current_user)):
    records=db.query(Analysis).filter(Analysis.user_id==user.id).all()
    return {"total":len(records),"flagged":sum("Unusual pattern" in a.result for a in records),"recent":[analysis_dict(a) for a in records[-5:][::-1]]}

@app.get("/api/model/info")
def model(): return model_info()

@app.post("/api/devices/register")
def register_device(data:DeviceIn, db:Session=Depends(get_db), user:User=Depends(current_user)):
    if data.device_key != DEVICE_API_KEY: raise HTTPException(401,"Device key does not match backend configuration")
    existing=db.query(Device).filter(Device.id==data.device_id).first()
    if existing and existing.user_id != user.id: raise HTTPException(409,"Device ID already belongs to another account")
    if not existing:
        db.add(Device(id=data.device_id,user_id=user.id,name=data.name,key_hash=digest(data.device_key)))
        db.commit()
    return {"device_id":data.device_id,"registered":True,"status":"Disconnected until first authenticated message arrives"}

@app.get("/api/devices")
def devices(db:Session=Depends(get_db), user:User=Depends(current_user)):
    return [{"device_id":d.id,"name":d.name,"connected":bool(d.connected),"last_seen":d.last_seen.isoformat() if d.last_seen else None,"selected_food":d.selected_food} for d in db.query(Device).filter(Device.user_id==user.id).all()]

@app.post("/api/sessions")
def create_session(data:SessionIn, db:Session=Depends(get_db), user:User=Depends(current_user)):
    device=db.query(Device).filter(Device.id==data.device_id,Device.user_id==user.id).first()
    if not device: raise HTTPException(404,"Registered device not found")
    if data.food not in PROFILES: raise HTTPException(422,"Unsupported food")
    sid=secrets.token_urlsafe(18)
    device.selected_food=data.food
    db.add(TestSession(id=sid,user_id=user.id,device_id=device.id,sample_id=data.sample_id,food=data.food))
    db.commit()
    return {"session_id":sid,"sample_id":data.sample_id,"food":data.food,"status":"active"}

@app.post("/api/sensors/ingest")
def ingest(data:IngestIn, x_device_id:str=Header(default=""), x_device_key:str=Header(default=""),
           db:Session=Depends(get_db)):
    device=db.query(Device).filter(Device.id==x_device_id).first()
    if not device or digest(x_device_key) != device.key_hash: raise HTTPException(401,"Unknown device or invalid device credentials")
    session=db.query(TestSession).filter(TestSession.id==data.session_id,TestSession.device_id==device.id,TestSession.status=="active").first()
    if not session: raise HTTPException(404,"No active test session for this device")
    if data.food != session.food: raise HTTPException(422,"Food profile does not match active test session")
    allowed=set(PROFILES[data.food]["features"])
    if not data.measurements or not set(data.measurements).issubset(allowed): raise HTTPException(422,"Measurement keys do not match the selected food profile")
    if any(not (-1e9 < float(v) < 1e9) for v in data.measurements.values()): raise HTTPException(422,"Invalid measurement value")
    if data.measured_at.tzinfo is None: raise HTTPException(422,"measured_at must include timezone information")
    reading=SensorReading(device_id=device.id,session_id=session.id,message_id=data.message_id,food=data.food,
      measured_at=data.measured_at,measurements_json=json.dumps(data.measurements))
    db.add(reading)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,"Duplicate message_id; reading already received")
    device.connected=True; device.last_seen=datetime.now(timezone.utc); db.commit()
    return {"accepted":True,"device_id":device.id,"session_id":session.id,"sample_id":session.sample_id,"measured_at":data.measured_at.isoformat(),"data_quality":"Accepted; schema and session checks passed","measurements":data.measurements}

@app.get("/api/sessions/{session_id}/readings")
def readings(session_id:str, db:Session=Depends(get_db), user:User=Depends(current_user)):
    session=db.query(TestSession).filter(TestSession.id==session_id,TestSession.user_id==user.id).first()
    if not session: raise HTTPException(404,"Session not found")
    items=db.query(SensorReading).filter(SensorReading.session_id==session_id).order_by(SensorReading.id.asc()).all()
    return [{"message_id":r.message_id,"measured_at":r.measured_at.isoformat(),"measurements":json.loads(r.measurements_json)} for r in items]

@app.post("/api/sessions/{session_id}/analyze")
def analyze_session(session_id:str, db:Session=Depends(get_db), user:User=Depends(current_user)):
    session=db.query(TestSession).filter(TestSession.id==session_id,TestSession.user_id==user.id).first()
    if not session: raise HTTPException(404,"Session not found")
    readings=db.query(SensorReading).filter(SensorReading.session_id==session_id).order_by(SensorReading.id.desc()).all()
    if not readings: raise HTTPException(422,"No sensor readings received for this test session")
    measurements=json.loads(readings[0].measurements_json)
    data=AnalyzeIn(sample_id=session.sample_id,food=session.food,mode="hardware",measurements=measurements)
    return analyze(data,db,user)
