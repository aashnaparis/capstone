import asyncio
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from snmp.trap import * # tailor better later
from net_monitor import monitor
from mqtt_net import mqtt_format
from database import zig_db, all_nodes, all_heartbeats, all_alarms, one_node, create_alert, create_heartbeat, create_network
import paho.mqtt.client as mqtt
import psycopg2
import asyncio
import os

load_dotenv()

app = FastAPI()

origins = ["http://localhost","http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#RECHECK
try:
    conn = zig_db()
    cursor = conn.cursor()
except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))
finally:
    cursor.close()
    conn.close()

def mqtt_thread():
    client = mqtt.Client()
    client.on_message = mqtt_format
    client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))
    client.subscribe(os.getenv("MQTT_TOPIC"))
    client.loop_forever()

#HTTP
@app.get("/node")
async def get_node():
    try:
        rows = await all_nodes()
         
        if rows is None:
            raise HTTPException(status_code=404, detail= "Node not found")
        
        info = []
        for row in rows:
            info.append({
                "node_id": row[0],
                "battery_mv": row[1],
                "status": row[2],
                "last_seen": row[3]
            })
        return info
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

@app.get("/node/{node_id}")
async def get_one_node(node_id: str):
    try:
        info = await one_node(node_id)

        if info is None:
            raise HTTPException(status_code=404, detail= "Node not found")
        
        return info
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))


@app.get("/alarm")
async def get_alarm():
    try:
        alarms = await all_alarms()

        if alarms is None:
            raise HTTPException(status_code=404, detail= "No alarm found")
        
        return alarms
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

@app.get("/heartbeat")
async def get_status():
    try:
        heartbeats = await all_heartbeats()

        if heartbeats is None:
            raise HTTPException(status_code=404, detail= "No heartbeat was sent")
    
        return heartbeats
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

@app.on_event("startup")
async def init_start():
    create_network()
    create_alert()
    create_heartbeat()
    asyncio.create_task(mqtt_thread())
    asyncio.create_task(monitor())
    



