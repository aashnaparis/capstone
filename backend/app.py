import asyncio
from fastapi import FastAPI, HTTPException, Body
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from snmp.trap import trap_caught
from net_monitor import monitor
from mqtt_net import mqtt_format
from database import all_nodes, all_heartbeats, all_alarms, all_stats, one_node, create_alert, create_heartbeat, create_network, create_user, create_stats, update_location, login_user
import paho.mqtt.client as mqtt
# from passlib.context import CryptContext
import bcrypt
import uuid
import os



load_dotenv()

app = FastAPI()

origins = ["http://localhost","http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(stored_hash, input_password):
#     return pwd_context.verify(input_password, stored_hash)

def verify_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(os.getenv("MQTT_TOPIC1"))
        client.subscribe(os.getenv("MQTT_TOPIC2"))
    else:
        print(f"Connection failed: {rc}")


async def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = mqtt_format
    client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))
    client.loop_start()

    while True:
        await asyncio.sleep(1)



#HTTP
@app.get("/node")
def get_node():
    try:
        rows = all_nodes()
         
        if rows is None:
            raise HTTPException(status_code=404, detail= "Node not found")
        
        info = []
        for row in rows:
            info.append({
                "node_id": row[0],
                "battery_mv": row[1],
                "status": row[2],
                "last_seen": row[3],
                "lat": row[4],
                "long": row[5]
            })
        return info
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))

@app.get("/node/{node_id}")
def get_one_node(node_id: str):
    try:
        info = one_node(node_id)

        if info is None:
            raise HTTPException(status_code=404, detail= "Node not found")
        
        return info
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))


@app.get("/alarm")
def get_alarm():
    try:
        alarms =  all_alarms()

        if alarms is None:
            raise HTTPException(status_code=404, detail= "No alarm found")
        data = [];
        for row in alarms:
            data.append({
                "id": row[0],
                "node_id": row[1],
                "battery_lvl": row[2],
                "severity": row[3],
                "timestamp": row[4]
            })
        return data
    except Exception as e:
         raise HTTPException(status_code = 500, detail=str(e))

@app.get("/heartbeat")
def get_status():
    try:
        heartbeats = all_heartbeats()

        if heartbeats is None:
            raise HTTPException(status_code=404, detail= "No heartbeat was sent")
        data = [];
        for row in heartbeats:
            data.append({
                "id": row[0],
                "node_id": row[1],
                "battery_lvl": row[2],
                "status": row[3],
                "timestamp": row[4]
            })
            
        return data
    except Exception as e:
         raise HTTPException(status_code = 500, detail=str(e))
    
@app.get("/stats")
def get_stats():
    try:
        stats = all_stats()

        if stats is None:
            raise HTTPException(status_code=404, detail= "No heartbeat was sent")
        data = [];
        for row in stats:
            data.append({
                "id": row[0],
                "node_id": row[1],
                "linkquality": row[2],
                "timestamp": row[3]
            })
            
        return data
    except Exception as e:
         raise HTTPException(status_code = 500, detail=str(e))

@app.put("/node/{node_id}/location")   
def select_location(node_id: str, lat: float = Body(...), lng: float = Body(...)):
    # try:
        update_location(node_id, lat, lng);
        return {"message": "Location updated"}
    # except Exception as e:
    #     raise HTTPException(status_code = 500, detail=str(e))

@app.post("/login")
def login(username: str = Body(...), password: str = Body(...)):
    try:
        user = login_user(username)

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        log_dict = {
            "user_id": user[0],
            "username": user[1],
            "password": user[2],
            "email": user[3],
        }
        

        if not verify_password(log_dict["password"], password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token = str(uuid.uuid4())
        
        return {"token": token, "user_id": log_dict["user_id"], "username": log_dict["username"], "email": log_dict["email"] }
        
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))
    
@app.get("/traps")
def get_traps():
    return trap_caught
    

@app.get("/status")
def status():

    try:

        data = {
            "nodes_online": 2,
            "active_alert": "NONE",
            "last_updated": "7:00 PM"
        }

        return data
    except Exception as e:

        return {
            "error": str(e)
        }

@app.on_event("startup")
async def init_start():
    create_network()
    create_alert()
    create_heartbeat()
    create_user()
    create_stats()
    asyncio.create_task(mqtt_thread())
    asyncio.create_task(monitor())
    



