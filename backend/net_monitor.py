from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import node_check, offline_update
from snmp.trap import dead_node_trap
import asyncio
import os

load_dotenv()

# function checking for node failure
def inspect_nodes():
    timeout_sec = int(os.getenv("HEARTBEAT_INTERVAL")) 
    threshold = datetime.utcnow() - timedelta(seconds=timeout_sec)
    dead_nodes = node_check(threshold)
    for node in dead_nodes:
        severity = os.getenv("SEVERITY_FAULT")
        # insert into node failure database
        offline_update(node.node_id)
        
        # send node failure snmp trap
        dead_node_trap(node.node_id, node.battery_lvl, severity)
        print(f"Node Failure, {node.node_id} : Severity, {severity}")

async def monitor():
    while True:
        asyncio.create_task(inspect_nodes())
        await asyncio.sleep(int(os.getenv("HEARTBEAT_TIMEOUT")))
            