# ☁️ Cloud & Infrastructure

> Estrategia de infraestructura física, local, cloud e híbrida para SBM Suite.
> 
> 
> Esta página define cómo distribuir hardware, servicios persistentes, cargas de IA, respaldos, movilidad, plataformas cloud y crecimiento futuro.
> 
> La arquitectura busca minimizar costos operacionales durante las primeras etapas, mantener control sobre servicios críticos y utilizar Azure o AWS solo cuando aporten una ventaja técnica, comercial, operativa o de portafolio.
> 

---

# 1. Objetivo

Construir una infraestructura híbrida capaz de soportar:

- desarrollo;
- pruebas;
- CI/CD;
- bases de datos;
- APIs;
- agentes IA;
- RAG;
- contenedores;
- Kubernetes;
- renderizado;
- IA generativa;
- almacenamiento;
- respaldos;
- trabajo remoto;
- despliegues cloud;
- crecimiento progresivo sin rediseñar toda la plataforma.

---

# 2. Principios

1. **Cloud-first cuando agrega valor**
    
    Utilizar servicios cloud cuando aporten disponibilidad, escalabilidad, alcance público, integración empresarial o evidencia profesional relevante.
    
2. **Local-first cuando reduce costos**
    
    Mantener localmente los servicios persistentes, laboratorios y cargas intensivas que no necesitan exposición pública permanente.
    
3. **Hybrid by design**
    
    La arquitectura debe funcionar de forma coherente entre infraestructura local, Azure y AWS.
    
4. **Portability**
    
    Los servicios deben empaquetarse con Docker y desplegarse sin acoplamiento innecesario a un proveedor.
    
5. **Separation of workloads**
    
    Separar aplicaciones, IA, almacenamiento, backups y renderizado.
    
6. **Low operating cost**
    
    Evitar servicios cloud permanentes que no generen valor real.
    
7. **Progressive growth**
    
    Comenzar con laboratorio personal y evolucionar hacia infraestructura empresarial.
    
8. **Security and observability**
    
    Toda infraestructura debe integrar controles de seguridad, logs, métricas y backups.
    
9. **Reproducibility**
    
    Configuración, despliegues e infraestructura deben versionarse.
    
10. **Portfolio evidence**
    
    Cada etapa debe producir evidencia técnica demostrable.
    

---

# 3. Arquitectura general

```
                           Internet
                              │
                 ┌────────────┴────────────┐
                 │                         │
              Azure                      AWS
                 │                         │
      Enterprise and Internal       Public and Customer
             Services                    Services
                 │                         │
                 └────────────┬────────────┘
                              │
                       Secure Connectivity
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
  Portable Local Server                       Home AI PC
         │                                         │
 APIs / Docker / K3s / DB                GPU / CUDA / Render
 CI/CD / Qdrant / Ollama                  ComfyUI / Blender
         │
         ▼
        NAS
         │
 Backups / Snapshots / Recovery
```

---

# 4. Modelo híbrido

## Infraestructura local

Se utilizará para:

- desarrollo;
- integración;
- laboratorios;
- servicios persistentes;
- Kubernetes local;
- bases de datos;
- RAG;
- agentes;
- observabilidad;
- CI/CD;
- IA local;
- pruebas de seguridad;
- almacenamiento;
- backups.

## Azure

Se utilizará principalmente para:

- servicios empresariales;
- Azure DevOps;
- Azure AI Foundry;
- Azure OpenAI;
- APIs internas cuando corresponda;
- agentes empresariales;
- integración Microsoft;
- servicios administrativos;
- demostraciones cloud.

## AWS

Se utilizará principalmente para:

- e-commerce;
- servicios públicos;
- APIs orientadas a clientes;
- Amazon Bedrock;
- Lambda;
- S3;
- EKS como etapa futura;
- especialización profesional;
- arquitectura multi-cloud selectiva.

---

# 5. Infraestructura local — Casa

## Objetivo

Disponer de una estación de trabajo dedicada a cargas pesadas de IA, renderizado, multimedia y experimentación con GPU.

## Equipamiento

| Priority | Equipment | Estimated Budget | Status |
| --- | --- | --- | --- |
| ⭐⭐⭐⭐⭐ | PC de IA y render | Hasta USD 5,000 | Planned |
| ⭐⭐⭐⭐⭐ | UPS dedicada | USD 300–600 | Planned |
| ⭐⭐⭐⭐☆ | Monitor adicional | Según necesidad | Planned |
| ⭐⭐⭐⭐☆ | Periféricos especializados | Según necesidad | Optional |

## Funciones

- Blender;
- ComfyUI;
- renderizado;
- generación de imágenes;
- generación de video;
- CUDA;
- entrenamiento e inferencia local;
- laboratorio GPU;
- computer vision;
- fine-tuning cuando sea viable;
- procesamiento multimedia.

## Requisitos recomendados

- GPU NVIDIA con suficiente VRAM;
- CPU multinúcleo;
- 64 GB RAM como base recomendada;
- NVMe rápido;
- buena ventilación;
- fuente certificada;
- UPS;
- acceso remoto seguro.

## Criterio de compra

La configuración exacta debe definirse al momento de comprar según:

- precio de GPU;
- VRAM;
- consumo;
- compatibilidad CUDA;
- disponibilidad local;
- necesidades reales de modelos;
- carga de Blender y ComfyUI.

---

# 6. Infraestructura de movilidad

## Objetivo

Mantener capacidad de trabajo remoto, desarrollo, conectividad y acceso seguro a la infraestructura.

## Equipamiento

| Priority | Equipment | Estimated Budget | Status |
| --- | --- | --- | --- |
| ⭐⭐⭐⭐⭐ | MacBook Pro M2 | Disponible | Active |
| ⭐⭐⭐⭐⭐ | Notebook Windows gamer | USD 2,000–3,000 | Planned |
| ⭐⭐⭐⭐⭐ | Jackery Explorer 1000 o equivalente | USD 900–1,100 | Planned |
| ⭐⭐⭐⭐☆ | Starlink Mini | USD 400–600 | Planned |

## Funciones

- desarrollo remoto;
- acceso seguro al servidor;
- pruebas Windows;
- renderizado ligero;
- ejecución de herramientas dependientes de NVIDIA;
- trabajo en terreno;
- continuidad energética;
- conexión de respaldo;
- administración remota.

## Principio

El notebook Windows no reemplaza al PC de IA. Su función es:

- movilidad;
- compatibilidad;
- pruebas;
- GPU portátil;
- desarrollo;
- contingencia.

---

# 7. Servidor portátil

## Objetivo

Crear un nodo físico compacto para ejecutar la plataforma local de SBM Suite.

## Configuración propuesta

| Priority | Equipment | Estimated Budget | Status |
| --- | --- | --- | --- |
| ⭐⭐⭐⭐⭐ | Minisforum MS-01 o equivalente vigente | USD 700–950 | Planned |
| ⭐⭐⭐⭐⭐ | 64 GB DDR5 | USD 180–230 | Planned |
| ⭐⭐⭐⭐⭐ | NVMe 2 TB para sistema | USD 170–220 | Planned |
| ⭐⭐⭐⭐⭐ | NVMe 4 TB para datos | USD 320–420 | Planned |
| ⭐⭐⭐⭐☆ | SSD externo de respaldo | USD 250–350 | Planned |

## Funciones

- Docker;
- Docker Compose;
- Kubernetes K3s;
- k3d;
- Proxmox;
- APIs;
- PostgreSQL;
- Qdrant;
- Redis;
- Celery;
- Kafka;
- Jenkins;
- SonarQube;
- Ollama;
- Prometheus;
- Grafana;
- Loki;
- Tempo;
- laboratorio local.

---

# 8. Arquitectura del servidor portátil

```
Physical Server
      │
      ├── Proxmox — Optional
      │      ├── VM Platform
      │      ├── VM Data
      │      └── VM Security Lab
      │
      └── Linux Host
             ├── Docker Compose
             ├── K3s / k3d
             ├── PostgreSQL
             ├── Qdrant
             ├── Redis
             ├── Kafka
             ├── Jenkins
             ├── SonarQube
             └── Observability
```

## Recomendación inicial

No utilizar Proxmox como requisito para comenzar.

Orden recomendado:

1. Linux directo;
2. Docker Compose;
3. k3d o K3s;
4. observabilidad;
5. Proxmox cuando exista una necesidad real de virtualización y aislamiento.

---

# 9. Distribución de almacenamiento del servidor

## NVMe 2 TB — Sistema

Usos:

- sistema operativo;
- herramientas;
- Docker;
- imágenes;
- configuraciones;
- código;
- CI/CD;
- aplicaciones.

## NVMe 4 TB — Datos

Usos:

- PostgreSQL;
- Qdrant;
- Kafka;
- artefactos;
- modelos;
- datasets;
- logs;
- métricas;
- respaldos temporales.

## SSD externo

Usos:

- respaldo local;
- imágenes de recuperación;
- exportaciones;
- transferencia;
- contingencia.

---

# 10. NAS

## Objetivo

Centralizar almacenamiento, snapshots, versionado y recuperación.

## Configuración propuesta

| Priority | Equipment | Estimated Budget | Status |
| --- | --- | --- | --- |
| ⭐⭐⭐⭐⭐ | Synology NAS de 4 bahías o equivalente | USD 700–900 | Planned |
| ⭐⭐⭐⭐⭐ | 2 × discos NAS de 8 TB | USD 350–500 | Planned |
| ⭐⭐⭐⭐☆ | Expansión futura de discos | Según necesidad | Planned |
| ⭐⭐⭐⭐☆ | UPS para NAS | Según necesidad | Planned |

## Funciones

- backups automáticos;
- snapshots;
- versionado;
- sincronización;
- almacenamiento documental;
- almacenamiento multimedia;
- respaldo de bases;
- respaldo de configuraciones;
- recuperación ante desastres.

---

# 11. Estrategia de backups

## Principio 3-2-1

- 3 copias;
- 2 medios distintos;
- 1 copia fuera del sitio.

## Diseño

```
Primary Data
    ↓
Local Backup
    ↓
NAS Snapshot
    ↓
Encrypted Off-Site Backup
```

## Datos a respaldar

- PostgreSQL;
- configuraciones;
- secretos cifrados;
- volúmenes;
- documentos;
- multimedia;
- Qdrant;
- modelos;
- datasets;
- Jenkins;
- SonarQube;
- Grafana;
- repositorios;
- Helm charts.

## Regla

El NAS no reemplaza un respaldo externo.

---

# 12. Energía y continuidad

## Equipamiento

- UPS para servidor;
- UPS para NAS;
- UPS para PC de IA;
- Jackery para movilidad;
- protección de voltaje;
- apagado controlado.

## Objetivos

- evitar corrupción;
- mantener servicios críticos;
- permitir apagado seguro;
- proteger hardware;
- soportar cortes breves;
- mantener conectividad básica.

---

# 13. Conectividad

## Componentes

- conexión de fibra principal;
- Starlink Mini como respaldo móvil;
- VPN;
- DNS;
- TLS;
- acceso remoto;
- segmentación de red.

## Acceso remoto

Debe utilizar:

- VPN;
- Tailscale como opción;
- WireGuard como opción;
- MFA;
- claves SSH;
- acceso administrativo restringido.

## Regla

No exponer directamente:

- PostgreSQL;
- Redis;
- Kafka;
- Qdrant;
- Jenkins;
- SonarQube;
- Proxmox;
- NAS.

---

# 14. Red local

## Segmentación recomendada

```
Management Network
Application Network
Data Network
AI and GPU Network
IoT or Guest Network
Backup Network
```

## Controles

- VLAN cuando el equipamiento lo permita;
- firewall;
- acceso mínimo;
- DNS interno;
- monitoreo;
- reservas DHCP;
- documentación de puertos;
- Wi-Fi separado para invitados.

---

# 15. Virtualización

## Proxmox

Estado:

- Planned;
- Optional;
- posterior a la estabilización del servidor.

## Casos

- aislamiento;
- laboratorios;
- snapshots;
- entornos separados;
- pruebas de seguridad;
- múltiples sistemas operativos;
- recuperación rápida.

## Riesgo

Agregar Proxmox demasiado pronto puede aumentar:

- complejidad;
- consumo de RAM;
- mantenimiento;
- dificultad de diagnóstico.

---

# 16. Contenedores

## Docker Compose

Será la base para:

- desarrollo;
- servicios locales;
- integración;
- laboratorios;
- despliegues simples.

## Kubernetes

Se utilizará para:

- aprendizaje;
- despliegue reproducible;
- escalado;
- health checks;
- ingress;
- Helm;
- observabilidad;
- seguridad;
- portafolio.

---

# 17. Kubernetes local

## Tecnologías

- K3s;
- k3d;
- Helm;
- ingress-nginx;
- cert-manager;
- Prometheus;
- Grafana;
- Loki;
- Tempo.

## Estrategia

1. comenzar con k3d;
2. desplegar aplicaciones stateless;
3. mantener PostgreSQL fuera del clúster inicialmente;
4. incorporar Redis y workers;
5. evaluar Kafka;
6. incorporar observabilidad;
7. agregar seguridad;
8. migrar cargas persistentes solo cuando sea necesario.

---

# 18. PostgreSQL

## Estrategia inicial

PostgreSQL permanecerá:

- en host local;
- en contenedor independiente;
- fuera del clúster;
- con backups automáticos;
- con acceso restringido.

## Futuro

Evaluar:

- réplica;
- alta disponibilidad;
- operador Kubernetes;
- servicio administrado cloud;
- failover.

---

# 19. Qdrant

## Estrategia

Qdrant puede ejecutarse:

- en Docker local;
- en K3s;
- en servidor portátil;
- con persistencia local;
- con backup de snapshots.

## Uso

- RAG;
- embeddings;
- filtros;
- documentos;
- memoria controlada.

---

# 20. Redis y Celery

## Infraestructura local

- Redis como broker y caché;
- Celery workers;
- Celery Beat;
- Flower.

## Despliegue

Primera etapa:

- Docker Compose.

Segunda etapa:

- Kubernetes.

---

# 21. Kafka

## Estrategia

Primera etapa:

- Docker Compose;
- KRaft;
- Kafka UI;
- Schema Registry.

Etapa posterior:

- Kubernetes;
- Strimzi;
- observabilidad;
- almacenamiento persistente.

## Regla

No incorporar Kafka antes de:

- estabilizar APIs;
- implementar Celery;
- definir eventos;
- implementar observabilidad.

---

# 22. PC de IA

## Separación de responsabilidades

El PC de IA no debe ser el servidor principal de aplicaciones.

## Uso

- inferencia GPU;
- ComfyUI;
- Blender;
- render;
- entrenamiento;
- generación multimedia;
- visión;
- fine-tuning;
- procesamiento por lotes.

## Integración

```
SBM Suite
    ↓
Internal AI API
    ↓
GPU Workstation
    ↓
Model or Render Job
    ↓
Result Storage
```

---

# 23. Modelos locales

## Herramientas

- Ollama;
- vLLM futuro;
- ComfyUI;
- Hugging Face;
- ONNX Runtime;
- PyTorch;
- TensorFlow.

## Usos

- desarrollo;
- fallback;
- privacidad;
- reducción de costos;
- pruebas;
- embeddings;
- inferencia;
- generación de medios.

---

# 24. Azure como plataforma principal

## Objetivo

Utilizar Azure como plataforma empresarial principal.

## Servicios prioritarios

- Azure DevOps;
- Azure Boards;
- Azure Repos;
- Azure Pipelines;
- Azure Wiki;
- Azure AI Foundry;
- Azure OpenAI;
- Azure Functions;
- Azure Blob Storage;
- Azure Monitor como investigación;
- Azure Container Registry como opción futura.

## Uso en SBM Suite

- gestión técnica;
- agentes IA;
- demos empresariales;
- integración Microsoft;
- procesos administrativos;
- servicios internos cuando corresponda.

---

# 25. Azure DevOps Free

## Uso

- backlog;
- repositorios;
- pipelines;
- wiki;
- dashboards;
- trazabilidad.

## Estrategia de costo

- Self-Hosted Agent;
- ejecución local;
- evitar agentes cloud innecesarios;
- mantener GitHub como vitrina;
- utilizar Azure DevOps como centro operativo.

---

# 26. Azure AI Foundry

## Uso

- aprendizaje;
- catálogo de modelos;
- prompts;
- agentes;
- evaluación;
- seguridad;
- despliegue;
- integración con `sbm-ai-assistant`.

## Formación prioritaria

- AI-3016;
- aplicaciones generativas;
- Azure AI Foundry;
- agentes;
- evaluaciones.

---

# 27. AWS como especialización

## Objetivo

Utilizar AWS donde aporte valor real y experiencia complementaria.

## Servicios

- S3;
- Lambda;
- API Gateway;
- Bedrock;
- EKS;
- CloudWatch;
- IAM;
- container registry;
- servicios públicos.

## Uso en SBM Suite

- e-commerce;
- APIs públicas;
- servicios cliente;
- contenido;
- archivos;
- agentes Bedrock;
- experimentación multi-cloud.

---

# 28. Estrategia multi-cloud

## Principio

Multi-cloud no significa duplicar toda la plataforma.

## Uso correcto

- Azure para gestión empresarial e IA Microsoft;
- AWS para servicios públicos, Bedrock y especialización;
- local para servicios persistentes, desarrollo y laboratorio.

## Evitar

- duplicar PostgreSQL sin necesidad;
- duplicar Kubernetes;
- mantener servicios inactivos pagos;
- agregar complejidad sin beneficio;
- crear dependencia circular.

---

# 29. Cloud connectivity

## Opciones

- VPN;
- WireGuard;
- Tailscale;
- private endpoints futuros;
- SSH tunnels controlados;
- API gateway;
- TLS mutuo como etapa avanzada.

## Casos

- cloud hacia servidor local;
- agentes cloud hacia APIs;
- pipelines;
- backups;
- administración;
- sincronización.

---

# 30. Domain and DNS

## Requisitos

- dominios por marca;
- subdominios;
- DNS central;
- TLS;
- renovaciones;
- separación de entornos.

## Ejemplo

```
api.sbm-suite.cl
manager.sbm-suite.cl
ai.sbm-suite.cl
store.ditalypasta.cl
staging-api.sbm-suite.cl
```

---

# 31. Storage strategy

| Storage Type | Use |
| --- | --- |
| NVMe local | Aplicaciones y datos activos |
| NAS | Backups y documentos |
| Object Storage | Archivos cloud |
| PostgreSQL | Datos transaccionales |
| Qdrant | Vectores |
| Kafka | Eventos temporales |
| Redis | Caché y estado temporal |
| Git | Código y configuración |

---

# 32. Disaster Recovery

## Escenarios

- pérdida de disco;
- pérdida del servidor;
- corrupción;
- robo;
- incendio;
- ransomware;
- error humano;
- pérdida de conectividad;
- caída cloud.

## Requisitos

- backups;
- snapshots;
- recuperación documentada;
- inventario;
- credenciales recuperables;
- infraestructura versionada;
- pruebas periódicas.

---

# 33. Recovery Objectives

## RPO

Define cuánto dato se puede perder.

## RTO

Define cuánto tiempo puede tardar la recuperación.

## Primera propuesta

| Service | RPO | RTO |
| --- | --- | --- |
| PostgreSQL | 24 h inicial | 4–8 h |
| Documentos | 24 h | 8 h |
| Código | Casi cero | 1 h |
| Configuración | Casi cero | 2 h |
| Qdrant | 24 h | 4 h |
| Multimedia | 24–72 h | 24 h |

---

# 34. Security

## Controles

- firewall;
- VPN;
- MFA;
- SSH keys;
- least privilege;
- secrets management;
- encrypted backups;
- disk encryption;
- VLAN;
- logs;
- updates;
- scans;
- hardening.

## Herramientas

- Trivy;
- Nmap;
- Wireshark;
- Gitleaks;
- Falco;
- Kubescape;
- kube-bench;
- Doppler.

---

# 35. Observability

## Infraestructura local

- Prometheus;
- Grafana;
- Loki;
- Tempo;
- Alertmanager;
- node exporter;
- cAdvisor;
- PostgreSQL exporter;
- Redis exporter.

## Hardware

Monitorear:

- temperatura;
- CPU;
- RAM;
- discos;
- SMART;
- red;
- energía;
- UPS;
- almacenamiento NAS;
- GPU.

---

# 36. Cost management

## Categorías

- hardware;
- energía;
- conectividad;
- almacenamiento;
- cloud;
- licencias;
- mantenimiento;
- reemplazo.

## Principios

- comprar por etapas;
- evitar sobreaprovisionar;
- priorizar hardware reusable;
- medir consumo;
- apagar recursos cloud;
- usar planes gratuitos;
- presupuestar respaldos;
- considerar costo eléctrico.

---

# 37. Presupuesto inicial estimado

| Area | Estimated Budget |
| --- | --- |
| Servidor portátil completo | USD 1,620–2,170 |
| SSD externo | USD 250–350 |
| NAS y discos iniciales | USD 1,050–1,400 |
| Movilidad y conectividad | USD 1,300–1,700 sin notebook |
| Notebook Windows | USD 2,000–3,000 |
| PC de IA | Hasta USD 5,000 |
| UPS | USD 300–600 por unidad según carga |

## Nota

Los valores son referenciales y deben actualizarse al momento de compra.

---

# 38. Prioridad de compra

## Etapa 1 — Servidor y movilidad

1. servidor portátil;
2. memoria;
3. almacenamiento NVMe;
4. SSD externo;
5. Jackery;
6. Starlink.

## Etapa 2 — Backups y plataforma

1. NAS;
2. discos;
3. UPS;
4. automatización de backups;
5. Azure DevOps;
6. Azure AI Foundry.

## Etapa 3 — IA y multimedia

1. PC de IA;
2. GPU;
3. UPS;
4. monitor;
5. almacenamiento adicional.

## Etapa 4 — Expansión

1. AWS;
2. multi-cloud;
3. rack;
4. networking avanzado;
5. oficina;
6. alta disponibilidad.

---

# 39. Roadmap técnico

## Fase 1 — Laboratorio actual

- MacBook;
- Docker Compose;
- repositorios;
- servicios locales;
- GitHub;
- Jenkins existente.

## Fase 2 — Servidor portátil

- Linux;
- Docker;
- PostgreSQL;
- Qdrant;
- Jenkins;
- SonarQube;
- Redis;
- Celery;
- observabilidad.

## Fase 3 — Kubernetes

- k3d;
- K3s;
- Helm;
- ingress;
- cert-manager;
- observabilidad;
- seguridad.

## Fase 4 — NAS y recuperación

- backups;
- snapshots;
- off-site;
- pruebas de recuperación.

## Fase 5 — Cloud

- Azure DevOps;
- Azure AI Foundry;
- APIs selectivas;
- AWS selectivo;
- conectividad híbrida.

## Fase 6 — GPU y media

- PC de IA;
- ComfyUI;
- Blender;
- modelos locales;
- render;
- generación multimedia.

---

# 40. Criterios para desplegar localmente

Un servicio debe permanecer local cuando:

- tiene uso constante;
- sería caro en cloud;
- no necesita exposición pública;
- contiene datos sensibles;
- requiere GPU local;
- es laboratorio;
- es herramienta interna;
- se puede operar de forma segura.

---

# 41. Criterios para desplegar en cloud

Un servicio debe ir a cloud cuando:

- necesita disponibilidad pública;
- necesita escalabilidad;
- necesita integración administrada;
- necesita alcance internacional;
- aporta evidencia profesional;
- requiere acceso desde clientes;
- necesita alta disponibilidad;
- el costo está justificado.

---

# 42. Criterios para no desplegar

No desplegar una tecnología solo porque:

- aparece en ofertas laborales;
- es popular;
- es enterprise;
- está disponible en free tier;
- permite decir que se utilizó.

Debe resolver un problema o demostrar una competencia con evidencia real.

---

# 43. Hardware as Portfolio Evidence

## Evidencia posible

- diagrama físico;
- inventario;
- rack o laboratorio;
- dashboards;
- clúster K3s;
- pipelines;
- pruebas de recuperación;
- monitoreo de UPS;
- servidor portátil;
- NAS;
- IA local;
- demo híbrida;
- documentación de costos.

---

# 44. Prioridad actual

## Urgente

1. definir especificaciones finales del servidor;
2. revisar alternativas vigentes al Minisforum MS-01;
3. calcular consumo;
4. definir sistema operativo;
5. diseñar almacenamiento;
6. preparar Compose transversal;
7. definir plan de backups.

## Corto plazo

1. comprar servidor;
2. instalar Linux;
3. desplegar servicios base;
4. configurar VPN;
5. configurar monitoreo;
6. configurar backups;
7. preparar Azure DevOps.

## Mediano plazo

1. NAS;
2. Kubernetes;
3. Redis;
4. Celery;
5. Kafka;
6. observabilidad completa;
7. Starlink;
8. Jackery.

## Largo plazo

1. PC de IA;
2. AWS;
3. multi-cloud;
4. rack;
5. alta disponibilidad;
6. oficina dedicada.

---

# 45. Criterio de finalización

Una capacidad de infraestructura se considera implementada cuando:

1. tiene propósito;
2. está documentada;
3. tiene seguridad;
4. tiene monitoreo;
5. tiene respaldo;
6. tiene recuperación;
7. tiene costos conocidos;
8. puede reproducirse;
9. puede mantenerse;
10. puede demostrarse.

---

# 46. Visión final

```
Local Infrastructure
        +
Azure Enterprise Platform
        +
AWS Public Services
        +
Portable Work Environment
        +
AI GPU Workstation
        +
NAS and Recovery
        +
Security and Observability
```

SBM Suite debe operar sobre una infraestructura híbrida, portátil, económica y escalable, capaz de crecer desde un laboratorio personal hacia una plataforma empresarial sin perder control, seguridad ni trazabilidad.

---

# 47. Production runtime baseline — 2026-08-16

Production runtime should prioritize brand APIs/channels, PostgreSQL, shared platform services and required async workers. SonarQube is a temporary QA workload and does not need permanent production uptime. Mobile binaries are distributed through mobile channels/stores rather than hosted as persistent VPS services. Capacity upgrades are driven by sustained CPU/RAM/I/O, queue lag and DB latency rather than the raw number of containers.
