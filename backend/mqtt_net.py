from database import zig_db, upsert_msg, upsert_alarm, upsert_heartbeat
from snmp.trap import alarm_trap, low_battery_trap, dead_battery_trap
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def mqtt_format(client, userdata, message):
    topic = message.topic
    payload = message.payload
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"{topic}:{payload.decode()} at {timestamp}")

    type_style = payload[0]
    node_id = payload[1]
    flagged = payload[2]
    battery_msb = payload[3]
    battery_lsb = payload[4]
    battery_lvl = int((battery_msb << 8) | battery_lsb)

    severity = determine_severity(type_style, flagged)

    #add query to insert into recieved packet database
    upsert_msg(node_id, type_style, battery_lvl, severity, timestamp)
    
    if severity == os.getenv("SEVERITY_CRITICAL"): 
        # insert into alarm database
        upsert_alarm(node_id, battery_lvl, timestamp)
        
        # send alarm snmp trap
        alarm_trap(node_id,severity)
    elif severity == os.getenv("SEVERITY_INFO"):
        # update timestamp in heartbeat database
        upsert_heartbeat(node_id, battery_lvl, timestamp)
    elif severity == os.getenv("SEVERITY_WARNING"):
        # send battery low snmp trap
        low_battery_trap(node_id, battery_lvl, severity)
    elif severity == os.getenv("SEVERITY_MAJOR"):
        # send battery dead
        dead_battery_trap(node_id, battery_lvl, severity)

def determine_severity(type, flag):
    if type == os.getenv("ALARM"):
        severity = os.getenv("SEVERITY_CRITICAL")  
    elif type == os.getenv("HEARTBEAT") and flag == 0x00:
        severity = os.getenv("SEVERITY_INFO")
    elif type == os.getenv("HEARTBEAT") and flag == 0x03:
        severity = os.getenv("SEVERITY_WARNING") #battery low
    elif type == os.getenv("HEARTBEAT") and flag == 0x04:
        severity = os.getenv("SEVERITY_MAJOR") #battery dead
    
    return severity
        