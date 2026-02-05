from pysnmp.hlapi import *
from dotenv import load_dotenv
from oid import *
import os

load_dotenv()

def alarm_trap(node_id,severity="CRITICAL"):
    sendNotification(
        SnmpEngine(),
        CommunityData(os.getenv("SNMP_PASSWORD")),
        UdpTransportTarget((os.getenv("SNMP_MANAGER"), os.getenv("SNMP_PORT"))),
        ContextData(),
        'trap',
        NotificationType(
            ObjectIdentity(ALARM_TRAP)
        ).addVarBinds(
            ('1.3.6.1.4.1.99999.1.1', OctetString(node_id)),
            ('1.3.6.1.4.1.99999.1.2', OctetString(severity)),
            ('1.3.6.1.4.1.99999.1.3', OctetString("Emergency Button Pressed"))
        )
    )

def low_battery_trap(node_id, battery_lvl, severity="WARNING"):
    sendNotification(
        SnmpEngine(),
        CommunityData(os.getenv("SNMP_PASSWORD")),
        UdpTransportTarget((os.getenv("SNMP_MANAGER"), os.getenv("SNMP_PORT"))),
        ContextData(),
        'trap',
        NotificationType(
            ObjectIdentity(LOW_BATTERY_TRAP)
        ).addVarBinds(
            ('1.3.6.1.4.1.99999.2.1', OctetString(node_id)),
            ('1.3.6.1.4.1.99999.2.2', OctetString(severity)),
            ('1.3.6.1.4.1.99999.2.3', Integer(battery_lvl))
        )
    )

def dead_battery_trap(node_id, battery_lvl, severity="MAJOR"):
    sendNotification(
        SnmpEngine(),
        CommunityData(os.getenv("SNMP_PASSWORD")),
        UdpTransportTarget((os.getenv("SNMP_MANAGER"), os.getenv("SNMP_PORT"))),
        ContextData(),
        'trap',
        NotificationType(
            ObjectIdentity(DEAD_BATTERY_TRAP)
        ).addVarBinds(
            ('1.3.6.1.4.1.99999.3.1', OctetString(node_id)),
            ('1.3.6.1.4.1.99999.3.2', OctetString(severity)),
            ('1.3.6.1.4.1.99999.3.3', Integer(battery_lvl))
        )
    )

def dead_node_trap(node_id, battery_lvl, severity="FAULT"):
    sendNotification(
        SnmpEngine(),
        CommunityData(os.getenv("SNMP_PASSWORD")),
        UdpTransportTarget((os.getenv("SNMP_MANAGER"), os.getenv("SNMP_PORT"))),
        ContextData(),
        'trap',
        NotificationType(
            ObjectIdentity(NODE_FAILURE_TRAP)
        ).addVarBinds(
            ('1.3.6.1.4.1.99999.4.1', OctetString(node_id)),
            ('1.3.6.1.4.1.99999.4.2', OctetString(severity)),
            ('1.3.6.1.4.1.99999.4.3', Integer(battery_lvl)),
            ('1.3.6.1.4.1.99999.4.4', OctetString("Node is offline"))
        )
    )