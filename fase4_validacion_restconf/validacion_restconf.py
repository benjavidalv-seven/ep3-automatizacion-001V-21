#!/usr/bin/env python3
"""
fase4_validacion_restconf/validacion_restconf.py
Validacion via RESTCONF - EP3 DRY7122
Alumno: Vidal Vidal Benjamin Jose | Codigo: 001V-21
"""

import socket
import os
import sys
import json
from datetime import datetime

import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_NAME = "validacion_restconf.py"
VARS_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../vars/vars_001V-21.yaml")
RESP_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencias/responses")

print("=" * 60)
print(f"  Script  : {SCRIPT_NAME}")
print(f"  Fecha   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Host VM : {socket.gethostname()}")
print("=" * 60)

with open(VARS_FILE, "r") as f:
    vars_data = yaml.safe_load(f)

alumno  = vars_data["alumno"]
router  = vars_data["router"]
cliente = vars_data["cliente"]

print(f"  Alumno  : {alumno['nombre']} ({alumno['codigo']})")
print(f"  Cliente : {cliente['empresa']}")
print(f"  Router  : {router['ip']}")
print()

EXPECTED = {
    "hostname":    router["hostname"],
    "loopback_ip": router["loopback_ip"],
    "desc_wan":    router["descripcion_wan"],
    "ntp_server":  router["ntp_server"],
}

BASE_URL = f"https://{router['ip']}/restconf/data"
AUTH     = (router["usuario"], router["password"])
HEADERS  = {"Accept": "application/yang-data+json"}

os.makedirs(RESP_DIR, exist_ok=True)

def restconf_get(endpoint, filename):
    url = f"{BASE_URL}/{endpoint}"
    print(f"  GET {url}")
    try:
        resp = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        filepath = os.path.join(RESP_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"       -> Guardado en {filename}")
        return data
    except Exception as e:
        print(f"       -> [ERROR] {e}")
        return None

print("Consultando endpoints RESTCONF...\n")

loopback_id    = router["loopback_id"]
data_hostname  = restconf_get("Cisco-IOS-XE-native:native/hostname", "get_hostname.json")
data_loopback  = restconf_get(f"ietf-interfaces:interfaces/interface=Loopback{loopback_id}", "get_loopback.json")
data_interfaces= restconf_get("ietf-interfaces:interfaces/interface=GigabitEthernet1", "get_interfaces.json")
data_ntp       = restconf_get("Cisco-IOS-XE-native:native/ntp", "get_ntp.json")

def safe_get(data, *keys):
    try:
        for key in keys:
            data = data[key]
        return str(data).strip() if data is not None else None
    except (KeyError, TypeError, IndexError):
        return None

got_hostname = safe_get(data_hostname, "Cisco-IOS-XE-native:hostname")
got_lb_ip    = safe_get(data_loopback, "ietf-interfaces:interface", "ietf-ip:ipv4", "address", 0, "ip")
got_desc_wan = safe_get(data_interfaces, "ietf-interfaces:interface", "description")
got_ntp      = safe_get(data_ntp, "Cisco-IOS-XE-native:ntp", "Cisco-IOS-XE-ntp:server", "server-list", 0, "ip-address")

print()
print("-" * 60)
print("  REPORTE DE VALIDACION RESTCONF")
print("-" * 60)

criteria = [
    ("Hostname corporativo", got_hostname, EXPECTED["hostname"]),
    ("IP Loopback",          got_lb_ip,   EXPECTED["loopback_ip"]),
    ("Descripcion WAN",      got_desc_wan,EXPECTED["desc_wan"]),
    ("Servidor NTP",         got_ntp,     EXPECTED["ntp_server"]),
]

passed = 0
for label, got, expected in criteria:
    status = "[OK]  " if got == expected else "[FAIL]"
    if got == expected:
        passed += 1
    print(f"  {status} {label}")
    print(f"         Esperado : {expected}")
    print(f"         Obtenido : {got}")
    print()

print("-" * 60)
total = len(criteria)
if passed == total:
    print(f"  RESULTADO: CONFORME ({passed}/{total} criterios OK)")
else:
    print(f"  RESULTADO: NO CONFORME ({passed}/{total} criterios OK)")
print("-" * 60)
