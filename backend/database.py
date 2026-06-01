import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os


def zig_db():
    return psycopg2.connect(
           database= os.getenv("DB_NAME"),
           user = os.getenv("DB_USER"),
           password = os.getenv("DB_PASSWORD"),
           host = os.getenv("DB_HOST"),
           port = os.getenv("DB_PORT")
)

def create_network():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS network (
            node_id TEXT PRIMARY KEY,
            type TEXT,
            battery_lvl INTEGER,
            severity TEXT,
            lat INTEGER,
            long INTEGER,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_alert():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert (
            id SERIAL PRIMARY KEY,
            node_id TEXT NOT NULL,
            battery_lvl INTEGER,
            severity TEXT,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_stats():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id SERIAL PRIMARY KEY,
            node_id TEXT NOT NULL,
            linkquality INTEGER,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_heartbeat():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat (
            id SERIAL PRIMARY KEY,
            node_id TEXT NOT NULL,
            battery_lvl INTEGER,
            status TEXT,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_user():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(25) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(25) UNIQUE NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()              
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def upsert_msg(node_id, type_style, battery_lvl, severity, timestamp):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO network (node_id, type, battery_lvl, severity, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(node_id)
        DO UPDATE SET
            battery_lvl = EXCLUDED.battery_lvl,
            type = EXCLUDED.type,
            severity = EXCLUDED.severity,
            timestamp = EXCLUDED.timestamp;""", (node_id,type_style,battery_lvl, severity, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def upsert_stat(node_id, linkquality, timestamp):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO stats (node_id, linkquality, timestamp)
        VALUES (%s, %s, %s)
       """, (node_id, linkquality, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def upsert_alarm(node_id, battery_lvl, severity, timestamp):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute(""" 
            INSERT INTO alert (node_id, battery_lvl, severity, timestamp)
            VALUES (%s, %s, %s, %s)
            """, (node_id, battery_lvl, severity, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def upsert_heartbeat(node_id, battery_lvl, timestamp):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO heartbeat (node_id, battery_lvl, status, timestamp)
            VALUES (%s, %s, 'ONLINE', %s)
            """, (node_id, battery_lvl, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def node_check(threshold):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT ON (node_id) node_id, battery_lvl, timestamp
        FROM heartbeat 
        WHERE status != 'OFFLINE'
        ORDER BY node_id, timestamp DESC
    """, (threshold,))
    all_nodes = cursor.fetchall()
    cursor.close()
    conn.close()

    dead_nodes = [(node_id, battery_lvl) for node_id, battery_lvl, timestamp in all_nodes if timestamp < threshold]
    return dead_nodes

def offline_update(node_id):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO heartbeat (node_id, battery_lvl, status, timestamp)
            SELECT node_id, battery_lvl, 'OFFLINE', NOW()
            FROM heartbeat
            WHERE node_id = %s
            ORDER BY timestamp DESC
            LIMIT 1""", (node_id,))
    conn.commit()
    cursor.close()
    conn.close()

def all_nodes():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT * from network""")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

    
def one_node(node_id):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT node_id FROM network WHERE node_id = %s""",(node_id,))
    info = cursor.fetchone()
    cursor.close()
    conn.close()
    return info

def update_location(node_id, lat, lng):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""UPDATE network SET lat=%s, long=%s WHERE node_id=%s""",(lat, lng, node_id))
    conn.commit()
    cursor.close()
    conn.close()

def login_user(username):
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id, username, password, email FROM users WHERE username = %s""",(username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def all_alarms():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM alert ORDER BY id DESC LIMIT 10""")
    alarms = cursor.fetchall()
    cursor.close()
    conn.close()
    return alarms

def all_heartbeats():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM heartbeat ORDER BY id DESC LIMIT 10""")
    heartbeats = cursor.fetchall()
    cursor.close()
    conn.close()
    return heartbeats

def all_stats():
    conn = zig_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM stats ORDER BY id DESC LIMIT 10""")
    stats = cursor.fetchall()
    cursor.close()
    conn.close()
    return stats
