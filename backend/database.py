import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os


def zig_db():
    return psycopg2.connect(
           database= os.getenv("DATABASE"),
           user = os.getenv("USER"),
           password = os.getenv("PASSWORD"),
           host = os.getenv("HOST")
)

def create_network():
    conn = zig_db()
    cursor = conn.cursor

    conn.execute("""
        CREATE TABLE IF NOT EXISTS network (
            node_id TEXT PRIMARY KEY,
            type TEXT,
            battery_lvl INTEGER,
            severity TEXT,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_alert():
    conn = zig_db()
    cursor = conn.cursor

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alert (
            node_id TEXT PRIMARY KEY,
            battery_lvl INTEGER,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_heartbeat():
    conn = zig_db()
    cursor = conn.cursor

    conn.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat (
            node_id TEXT PRIMARY KEY,
            battery_lvl INTEGER,
            status TEXT,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def upsert_msg(type, node_id, battery_lvl, severity, timestamp):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""
        INSERT INTO network (node_id, type, battery_lvl, severity, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(node_id)
        DO UPDATE SET
            battery = EXCLUDED.battery_lvl,
            type = EXCLUDED.type,
            severity = EXCLUDED.severity,
            timestamp = EXCLUDED.timestamp;""", (type, node_id, battery_lvl, severity, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def upsert_alarm(node_id, battery_lvl, timestamp):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute(""" 
            INSERT INTO alert (node_id, battery_lvl, timestamp)
            VALUES (%s, %s, %s)
            ON CONFLICT(node_id)
            DO UPDATE SET
                battery = EXCLUDED.battery_lvl,
                timestamp = EXCLUDED.timestamp;""", (node_id, battery_lvl, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def upsert_heartbeat(node_id, battery_lvl, timestamp):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""
            INSERT INTO heartbeat (node_id, battery_lvl, status, timestamp)
            VALUES (%s, %s, "ONLINE", %s)
            ON CONFLICT(node_id)
            DO UPDATE SET
                battery = EXCLUDED.battery_lvl,
                timestamp = EXCLUDED.timestamp;""", (node_id, battery_lvl, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def node_check(threshold):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""
        SELECT node_id 
        FROM heartbeat 
        WHERE timestamp < %s
        AND status != 'OFFLINE'
    """, (threshold))
    dead_nodes = cursor.fetchall()
    return dead_nodes
    

def offline_update(node_id):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""
            UPDATE nodes
            SET status = 'OFFLINE'
            WHERE node_id = %s""", (node_id))
    conn.commit()
    cursor.close()
    conn.close()

def all_nodes():
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""SELECT * from heartbeat""")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

    
def one_node(node_id):
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""SELECT node_id FROM network WHERE node_id = %s""",(node_id))
    info = cursor.fetchone()
    return info

def all_alarms():
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""SELECT * FROM alert""")
    alarms = cursor.fetchall()
    return alarms

def all_heartbeats():
    conn = zig_db()
    cursor = conn.cursor
    cursor.execute("""SELECT * FROM heartbeat""")
    heartbeats = cursor.fetchall()
    return heartbeats
