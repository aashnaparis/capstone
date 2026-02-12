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
            (ALARM_TRAP_NODE, OctetString(node_id)),
            (ALARM_TRAP_SEV, OctetString(severity)),
            (ALARM_TRAP_MSG, OctetString("Emergency Button Pressed"))
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
            (LOW_BATT_NODE, OctetString(node_id)),
            (LOW_BATT_SEV, OctetString(severity)),
            (LOW_BATT_BATT, Integer(battery_lvl))
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
            (DEAD_BATT_NODE, OctetString(node_id)),
            (DEAD_BATT_SEV, OctetString(severity)),
            (DEAD_BATT_BATT, Integer(battery_lvl))
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
            (FAIL_NODE, OctetString(node_id)),
            (FAIL_SEV, OctetString(severity)),
            (FAIL_BATT, Integer(battery_lvl)),
            (FAIL_MSG, OctetString("Node is offline"))
        )
    )
    