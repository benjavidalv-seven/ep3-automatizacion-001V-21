#!/usr/bin/env python3
"""
fase5_reporte/generar_certificado.py
Generador de certificado de compliance - EP3 DRY7122
Alumno: Vidal Vidal Benjamin Jose | Codigo: 001V-21
"""

import os
import socket
from datetime import datetime
import yaml

VARS_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../vars/vars_001V-21.yaml")
OUTPUT_NETCONF  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt")
OUTPUT_RESTCONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt")
DIFF_DIR        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencias/diff_001V-21")
CERT_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencias/certificado_compliance_001V-21.txt")

with open(VARS_FILE, "r") as f:
    vars_data = yaml.safe_load(f)

alumno  = vars_data["alumno"]
router  = vars_data["router"]
cliente = vars_data["cliente"]

def check_conforme(filepath, label):
    if not os.path.exists(filepath):
        print(f"  [WARN] No se encontro: {filepath}")
        return False
    with open(filepath, "r") as f:
        content = f.read()
    if "RESULTADO: CONFORME" in content:
        print(f"  [OK]   {label}: CONFORME")
        return True
    print(f"  [FAIL] {label}: NO CONFORME")
    return False

def check_diff():
    if not os.path.exists(DIFF_DIR):
        print(f"  [WARN] Directorio diff no encontrado")
        return False
    files = [f for f in os.listdir(DIFF_DIR) if os.path.getsize(os.path.join(DIFF_DIR, f)) > 0]
    if files:
        print(f"  [OK]   Diff detectado ({len(files)} archivo(s) con cambios)")
        return True
    print("  [WARN] Sin cambios detectados en diff")
    return False

print("=" * 60)
print("  GENERANDO CERTIFICADO DE COMPLIANCE")
print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print()

netconf_ok  = check_conforme(OUTPUT_NETCONF,  "Validacion NETCONF")
restconf_ok = check_conforme(OUTPUT_RESTCONF, "Validacion RESTCONF")
diff_ok     = check_diff()

global_ok = netconf_ok and restconf_ok and diff_ok
resultado = "CONFORME" if global_ok else "NO CONFORME"

now = datetime.now()

certificado = f"""
================================================================================
         CERTIFICADO DE COMPLIANCE - EP3 DRY7122
         DUOC UC - Escuela de Informatica y Telecomunicaciones
================================================================================

  DATOS DEL ALUMNO
  ----------------
  Nombre    : {alumno['nombre']}
  Codigo    : {alumno['codigo']}
  Asignatura: DRY7122 - Programacion y Redes Virtualizadas (SDN-NFV)

  DATOS DEL PROYECTO
  ------------------
  Empresa cliente : {cliente['empresa']}
  Hostname router : {router['hostname']}
  IP Loopback     : {router['loopback_ip']}/{router['loopback_prefix']}
  Desc. WAN       : {router['descripcion_wan']}
  Banner          : {router['banner']}
  Servidor NTP    : {router['ntp_server']}

  RESULTADOS DE VALIDACION
  ------------------------
  Validacion NETCONF   : {"CONFORME" if netconf_ok  else "NO CONFORME"}
  Validacion RESTCONF  : {"CONFORME" if restconf_ok else "NO CONFORME"}
  Diff baseline/final  : {"CAMBIOS DETECTADOS" if diff_ok else "SIN CAMBIOS"}

  RESULTADO GLOBAL
  ----------------

  >>> {resultado} <

  El equipo {router['hostname']} {'ha sido configurado correctamente y queda' if global_ok else 'NO cumple con los criterios y NO esta'}
  {'listo para operar en la red de ' + cliente['empresa'] + '.' if global_ok else 'listo para operar.'}

  Fecha y hora de emision : {now.strftime('%Y-%m-%d %H:%M:%S')}
  Host de emision         : {socket.gethostname()}
  Generado por            : generar_certificado.py

================================================================================
"""

os.makedirs(os.path.dirname(CERT_FILE), exist_ok=True)
with open(CERT_FILE, "w") as f:
    f.write(certificado)

print()
print(certificado)
print(f"Certificado guardado en: {CERT_FILE}")
