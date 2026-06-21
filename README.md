
# EP3 — Implementación de Automatización de Red con Compliance Auditado

**Alumno:** Vidal Vidal Benjamin Jose | **Código:** 001V-21
**Asignatura:** DRY7122 — Programación y Redes Virtualizadas (SDN-NFV)
**DUOC UC — Escuela de Informática y Telecomunicaciones**

---

## 1. Objetivo del proyecto

Se implementó la incorporación automatizada de un router Cisco CSR1000v a la red corporativa de **Integración Digital SA**. El objetivo fue ejecutar el ciclo completo de aprovisionamiento: documentar el estado inicial del equipo, aplicar la configuración estándar de la empresa mediante herramientas de automatización, y verificar de forma independiente que todos los parámetros quedaron correctamente configurados antes de entregar el equipo a operaciones.

---

## 2. Alcance

**Dentro del alcance:**
- Captura del estado inicial (baseline) del router antes de cualquier cambio
- Habilitación de servicios de automatización: NETCONF y RESTCONF
- Aplicación de configuración corporativa: hostname, banner, NTP, descripción WAN e interfaz Loopback de gestión
- Validación independiente vía NETCONF y RESTCONF
- Generación de certificado de compliance

**Fuera del alcance:** routing dinámico, QoS, ACLs, monitoreo SNMP.

**Herramientas:** pyATS/Genie, Ansible, ncclient, Python requests, GitHub.

---

## 3. Infraestructura utilizada

| Componente | Detalle |
|---|---|
| Router | Cisco CSR1000v (IOS-XE) — IP 192.168.56.101 |
| Estación de trabajo | DEVASC VM (Ubuntu) — hostname labvm |
| Python | 3.x |
| pyATS / Genie | Instalado en la VM |
| Ansible | ansible-core con colección cisco.ios |
| ncclient | Conexión NETCONF puerto 830 |
| requests | Consultas RESTCONF HTTPS |
| Control de versiones | GitHub — ep3-automatizacion-001V-21 |

---

## 4. Tecnologías empleadas y justificación

**pyATS/Genie:** Se usó en Fase 1 y 5 para capturar snapshots del router via SSH sin requerir NETCONF habilitado, y comparar diferencias entre estados con genie diff.

**Ansible:** Se usó en Fase 2 porque permite definir configuración de forma declarativa e idempotente, garantizando reproducibilidad.

**NETCONF:** Se usó en Fase 3 como protocolo independiente de validación. Opera en puerto 830 y retorna configuración completa en XML.

**RESTCONF:** Se usó en Fase 4 como segunda validación independiente. Expone recursos via URLs REST sobre HTTPS retornando JSON.

---

## 5. Configuración aplicada

| Parámetro | Valor configurado |
|---|---|
| Hostname corporativo | RTR-INTDIG |
| IP Loopback (Loopback21) | 10.1.21.1 / 255.255.255.0 |
| Descripción GigabitEthernet1 | Enlace-WAN-Tocopilla |
| Banner de acceso (MOTD) | ACCESO RESTRINGIDO - INTDIG |
| Servidor NTP | 1.1.1.1 |
| NETCONF | Habilitado |
| RESTCONF | Habilitado |

---

## 6. Resultados de validación

| Criterio | NETCONF | RESTCONF |
|---|---|---|
| Hostname (RTR-INTDIG) | CONFORME | CONFORME |
| IP Loopback (10.1.21.1) | CONFORME | CONFORME |
| Máscara Loopback (255.255.255.0) | CONFORME | — |
| Descripción WAN | CONFORME | CONFORME |
| Servidor NTP (1.1.1.1) | CONFORME | CONFORME |

---

## 7. Conclusiones

El router **RTR-INTDIG** fue aprovisionado exitosamente con la configuración corporativa de **Integración Digital SA**. Las validaciones via NETCONF (5/5) y RESTCONF (4/4) confirmaron conformidad total. El equipo se entrega a operaciones en estado **CONFORME**.
