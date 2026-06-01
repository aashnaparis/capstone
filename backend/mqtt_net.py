from database import zig_db, upsert_msg, upsert_alarm, upsert_heartbeat, upsert_stat
from snmp.trap import alarm_trap, low_battery_trap, dead_battery_trap
from datetime import datetime
from dotenv import load_dotenv
import json
import os

load_dotenv()

def mqtt_format(client, userdata, message):
    topic = message.topic
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        data = json.loads(message.payload.decode()) 
        payload = bytes.fromhex(data['raw_payload'])
        lqi = data.get("linkquality")
    except Exception as e:
        payload = message.payload
        print(f"Error, {e}")
        
    hex_str = ' '.join(f'{b:02x}' for b in payload)
    print(f"{topic}:{hex_str} at {timestamp}")

    if not payload or len(payload) == 0:
        print(f"Warning: Empty Message on Topic, {message.topic}")
        return
    
    type_style = payload[0]
    node_id = payload[1]
    flagged = payload[2]
    battery_msb = payload[3]
    battery_lsb = payload[4]
    battery_lvl = int((battery_msb << 8) | battery_lsb)
    linkquality = lqi
    # rssi = None

    print(f"lqi:{linkquality} ")
    print(f"frame_type:{type_style} at flag: {flagged}")
    severity = determine_severity(type_style, flagged)

    #add query to insert into recieved packet database
    upsert_msg(node_id, type_style, battery_lvl, severity, timestamp)
    
    upsert_stat(node_id, linkquality, timestamp) 
    
    if severity == int(os.getenv("SEVERITY_CRITICAL")): 
        # insert into alarm database
        upsert_alarm(node_id, battery_lvl, severity, timestamp)
        # send alarm snmp trap
        alarm_trap(node_id,battery_lvl, severity)
    elif severity == int(os.getenv("SEVERITY_INFO")):
        # update timestamp in heartbeat database
        upsert_heartbeat(node_id, battery_lvl, timestamp)
    elif severity == int(os.getenv("SEVERITY_WARNING")):
        upsert_alarm(node_id, battery_lvl, severity, timestamp)
        # send battery low snmp trap
        low_battery_trap(node_id, battery_lvl, severity)
    elif severity == int(os.getenv("SEVERITY_MAJOR")):
        upsert_alarm(node_id, battery_lvl, severity, timestamp)
        # send battery dead
        dead_battery_trap(node_id, battery_lvl, severity)

def determine_severity(type, flag):
    severity = None
    if type == int(os.getenv("ALARM")):
        severity = int(os.getenv("SEVERITY_CRITICAL"))  
    elif type == int(os.getenv("HEARTBEAT")):
        if flag & 0x02:
            severity = int(os.getenv("SEVERITY_INFO"))
        if flag & 0x04:
            severity = int(os.getenv("SEVERITY_WARNING"))
        if flag & 0x08:
            severity = int(os.getenv("SEVERITY_INFO"))
    
    return severity
        