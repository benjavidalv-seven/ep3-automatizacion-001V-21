#!/usr/bin/env python3
"""
fase3_validacion_netconf/validacion_netconf.py
Validacion via NETCONF - EP3 DRY7122
Alumno: Vidal Vidal Benjamin Jose | Codigo: 001V-21
"""

import socket
import os
import sys
from datetime import datetime

import yaml
from ncclient import manager
from lxml import etree

SCRIPT_NAME = "validacion_netconf.py"
VARS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../vars/vars_001V-21.yaml")
OUTPUT_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencias/rpc_reply_raw.xml")

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

EXPECTED = {
    "hostname":      router["hostname"],
    "loopback_ip":   router["loopback_ip"],
    "loopback_mask": router["loopback_mask"],
    "desc_wan":      router["descripcion_wan"],
    "ntp_server":    router["ntp_server"],
}

print(f"  Alumno  : {alumno['nombre']} ({alumno['codigo']})")
print(f"  Cliente : {cliente['empresa']}")
print(f"  Router  : {router['ip']}:830")
print()

NETCONF_FILTER = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <ntp/>
    <interface>
      <GigabitEthernet>
        <name>1</name>
        <description/>
      </GigabitEthernet>
      <Loopback>
        <name/>
        <ip/>
      </Loopback>
    </interface>
  </native>
</filter>
"""

print("Conectando al router via NETCONF (puerto 830)...")

try:
    with manager.connect(
        host=router["ip"],
        port=830,
        username=router["usuario"],
        password=router["password"],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
    ) as m:
        print("Conexion NETCONF establecida.\n")
        reply = m.get_config(source="running", filter=NETCONF_FILTER)
        xml_raw = reply.xml
        os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)
        with open(OUTPUT_XML, "w") as f:
            f.write(xml_raw)
        print(f"XML guardado en: {OUTPUT_XML}\n")

        root = etree.fromstring(xml_raw.encode())
        ns = {
            "nc":     "urn:ietf:params:xml:ns:netconf:base:1.0",
            "native": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
        }

        def xpath(expr):
            results = root.xpath(expr, namespaces=ns)
            return results[0].text.strip() if results and results[0].text else None

        got_hostname = xpath(".//native:native/native:hostname")
        ns_ntp = {
            "nc":     "urn:ietf:params:xml:ns:netconf:base:1.0",
            "native": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
            "ntp":    "http://cisco.com/ns/yang/Cisco-IOS-XE-ntp",
        }
        ntp_results = root.xpath(".//native:native/native:ntp/ntp:server/ntp:server-list/ntp:ip-address", namespaces=ns_ntp)
        got_ntp = ntp_results[0].text.strip() if ntp_results and ntp_results[0].text else None
        got_desc_wan = xpath(".//native:native/native:interface/native:GigabitEthernet[native:name='1']/native:description")
        loopback_id  = str(router["loopback_id"])
        got_lb_ip    = xpath(f".//native:native/native:interface/native:Loopback[native:name='{loopback_id}']/native:ip/native:address/native:primary/native:address")
        got_lb_mask  = xpath(f".//native:native/native:interface/native:Loopback[native:name='{loopback_id}']/native:ip/native:address/native:primary/native:mask")

except Exception as e:
    print(f"[ERROR] Fallo la conexion NETCONF: {e}")
    sys.exit(1)

print("-" * 60)
print("  REPORTE DE VALIDACION NETCONF")
print("-" * 60)

criteria = [
    ("Hostname corporativo",  got_hostname, EXPECTED["hostname"]),
    ("IP Loopback",           got_lb_ip,    EXPECTED["loopback_ip"]),
    ("Mascara Loopback",      got_lb_mask,  EXPECTED["loopback_mask"]),
    ("Descripcion WAN",       got_desc_wan, EXPECTED["desc_wan"]),
    ("Servidor NTP",          got_ntp,      EXPECTED["ntp_server"]),
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
