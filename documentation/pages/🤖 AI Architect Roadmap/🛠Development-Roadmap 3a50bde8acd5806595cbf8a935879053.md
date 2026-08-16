# 🛠Development-Roadmap

> **Nota de arquitectura 2026-08-16:** `sbm-comercial` y `sbm-digital-api` se conservan solo como conceptos históricos del roadmap. No son proyectos aprobados para crear actualmente; el diseño vigente prioriza APIs de marca + stores/mobile/client channels directos.
>
> Roadmap técnico y funcional de evolución de SBM Suite.
> 
> 
> Esta página define el orden de implementación de la plataforma completa. La visión incluye todos los módulos futuros, pero la ejecución mantiene una prioridad estricta: primero estabilizar arquitectura, QA, seguridad, documentación e integración; después incorporar infraestructura distribuida, observabilidad, IA avanzada, comercio, marketing, operaciones, finanzas y contabilidad.
> 

---

# 1. Estado actual

## Desarrollo activo

Actualmente el trabajo se concentra en:

- separación de responsabilidades entre `sbm-api` y `dp-api`;
- migración de endpoints y procesos públicos desde `sbm-api` hacia `dp-api`;
- eliminación futura de duplicaciones;
- estabilización de los módulos `product` y `material`;
- integración funcional de `dp-api` con `sbm-manager`;
- preparación del estándar transversal de QA y seguridad;
- documentación técnica por repositorio;
- planificación de migración hacia Azure DevOps.

## Estado de `sbm-ai-assistant`

Actualmente incluye:

- RAG documental;
- integración con Confluence;
- embeddings;
- Qdrant;
- Slack como interfaz;
- Cohere como LLM;
- sincronización programada de documentación.

La siguiente etapa es conectar el asistente con:

1. `sbm-api`;
2. `dp-api`.

---

# 2. Principios del roadmap

1. La visión completa de SBM Suite debe permanecer documentada desde el inicio.
2. La prioridad de implementación no cambia por agregar módulos futuros.
3. No se continúa creando módulos de negocio sin una base mínima de QA y seguridad.
4. Cada tecnología debe resolver un problema real o demostrar una competencia relevante.
5. Los módulos críticos deben incorporar trazabilidad, permisos y aprobación humana.
6. Las nuevas APIs cliente solo se crean cuando exista una necesidad funcional real.
7. La arquitectura hexagonal se aplica a módulos con reglas de negocio; los módulos genéricos pueden mantener arquitectura por capas.
8. Las herramientas del portafolio deben priorizar opciones gratuitas, locales, open source o self-hosted.
9. Notion mantiene la visión general; Azure DevOps y los repositorios asumirán progresivamente la documentación técnica.
10. La formación y las certificaciones avanzan en paralelo al desarrollo.

---

# 3. Fase 0 — Formación urgente y preparación Azure

## Objetivo

Preparar el entorno Microsoft y comenzar la certificación prioritaria sin detener el desarrollo local.

## Tareas

1. Crear o validar la cuenta Microsoft utilizada para formación.
2. Inscribirse en:
    - **AI-3016: Develop generative AI apps in Azure AI Foundry portal**.
3. Crear una organización en Azure DevOps Free.
4. Crear el proyecto SBM Suite.
5. Configurar inicialmente:
    - Azure Boards;
    - Azure Repos;
    - Azure Wiki;
    - Azure Pipelines;
    - dashboards.
6. Definir la estrategia de convivencia entre GitHub y Azure DevOps.
7. Mantener GitHub como vitrina pública.
8. Utilizar Azure DevOps como plataforma empresarial de gestión y CI/CD.
9. Preparar un Self-Hosted Agent para evitar infraestructura cloud permanente.
10. Documentar posteriormente la aplicación de Azure AI Foundry dentro de `sbm-ai-assistant`.

## Resultado esperado

- certificación iniciada;
- entorno Azure preparado;
- proyecto SBM Suite creado;
- estrategia documental y de repositorios definida.

---

# 4. Fase 1 — Separación de APIs y estabilización del núcleo

## Objetivo

Finalizar la separación funcional entre la API interna y la primera API cliente.

## `sbm-api`

Debe conservar:

- procesos internos;
- procesos críticos;
- administración SBM;
- lógica transversal;
- configuración;
- franquicias y marcas;
- inventario interno;
- cálculos;
- fiscal;
- operaciones;
- integraciones internas;
- funciones no expuestas directamente al cliente.

## `dp-api`

Debe concentrar:

- primera API cliente de SBM Suite;
- productos;
- materiales;
- catálogos;
- precios públicos;
- pedidos;
- clientes;
- proveedores;
- sucursales;
- tickets;
- servicios;
- funcionalidades públicas de Ditaly Pasta.

## Tareas

1. Inventariar endpoints actuales de ambas APIs.
2. Clasificar cada endpoint como:
    - interno;
    - público;
    - compartido;
    - duplicado;
    - obsoleto.
3. Migrar a `dp-api` los endpoints públicos aún existentes en `sbm-api`.
4. Eliminar implementaciones duplicadas una vez validadas.
5. Revisar serializers, modelos y permisos.
6. Definir contratos OpenAPI.
7. Documentar dependencias entre servicios.
8. Definir tratamiento de usuarios y selección de marca.
9. Validar `product` y `material` de extremo a extremo.
10. Preparar integración síncrona y asíncrona futura.

## Resultado esperado

- responsabilidades claras;
- endpoints sin duplicación;
- contratos documentados;
- `product` y `material` estables;
- base preparada para nuevos módulos.

---

# 5. Fase 2 — Estándar transversal de QA

## Objetivo

Crear una estructura de calidad aplicable a todos los proyectos, no solo a Django.

## Alcance

- `sbm-manager`;
- `sbm-api`;
- `dp-api`;
- `sbm-ai-assistant`;
- `sbm-db`;
- `sbm-comercial`;
- futuras APIs y aplicaciones;
- infraestructura;
- integraciones;
- flujos IA.

## Tareas principales

1. Definir la política general de QA.
2. Definir niveles mínimos de cobertura.
3. Implementar pruebas unitarias.
4. Implementar pruebas de integración.
5. Implementar pruebas de contrato.
6. Implementar pruebas E2E.
7. Implementar pruebas de migraciones.
8. Implementar pruebas de carga.
9. Integrar SonarQube Community Build.
10. Configurar Quality Gates.
11. Generar reportes automáticos.
12. Integrar QA en pull requests y pipelines.

## Tecnologías iniciales

### Python y Django

- pytest;
- pytest-django;
- pytest-cov;
- pytest-asyncio;
- Factory Boy;
- Faker;
- Testcontainers.

### Vue

- Vitest;
- Vue Test Utils;
- Mock Service Worker;
- Playwright.

### React

- Vitest;
- React Testing Library;
- Mock Service Worker;
- Playwright.

### Node.js

- Jest;
- Supertest;
- Testcontainers.

### API

- Bruno;
- Postman Free;
- Newman;
- OpenAPI contract testing;
- Pact.

### Performance

- k6;
- Locust como alternativa opcional.

### Calidad

- SonarQube Community Build;
- SonarScanner;
- Ruff;
- Black;
- mypy;
- ESLint;
- Prettier.

## Resultado esperado

- estándar QA documentado;
- pipelines con pruebas;
- cobertura visible;
- Quality Gate;
- base segura para continuar el desarrollo funcional.

---

# 6. Fase 3 — Seguridad y DevSecOps

## Objetivo

Integrar seguridad durante todo el ciclo de desarrollo.

## Flujo

```
Diseño
   ↓
Threat Modeling
   ↓
Desarrollo
   ↓
SAST y Secret Scanning
   ↓
Pruebas
   ↓
Dependency Scanning
   ↓
Build de contenedor
   ↓
Container Scanning
   ↓
Despliegue
   ↓
DAST
   ↓
Runtime Monitoring
```

## Tareas

1. Definir amenazas por aplicación.
2. Aplicar OWASP Top 10 y OWASP API Security Top 10.
3. Integrar SAST.
4. Escanear dependencias.
5. Detectar secretos.
6. Escanear imágenes Docker.
7. Validar configuraciones Kubernetes.
8. Ejecutar DAST.
9. Validar seguridad de APIs.
10. Incorporar seguridad específica para LLM.
11. Configurar auditoría.
12. Bloquear pipelines ante vulnerabilidades críticas.

## Herramientas gratuitas o locales

- Semgrep Community;
- Bandit;
- ESLint Security;
- pip-audit;
- npm audit;
- Dependabot;
- OWASP Dependency-Check;
- Gitleaks;
- TruffleHog OSS;
- Trivy;
- OWASP ZAP;
- Burp Suite Community;
- Kubescape;
- kube-bench;
- kube-score;
- Falco;
- Nmap;
- Wireshark;
- Maltego Community;
- Garak;
- Promptfoo OSS.

## Resultado esperado

- flujo DevSecOps activo;
- seguridad integrada en PR y CI/CD;
- reportes por proyecto;
- protección de APIs, contenedores, dependencias y agentes IA.

---

# 7. Fase 4 — Documentación y migración hacia Azure DevOps

## Objetivo

Distribuir correctamente la documentación y reducir progresivamente el contenido técnico de Notion.

## Notion

Mantendrá:

- visión general;
- roadmap;
- prioridades;
- aprendizaje;
- certificaciones;
- estado ejecutivo;
- arquitectura de alto nivel.

## Azure DevOps Wiki

Contendrá:

- arquitectura técnica;
- ADRs;
- integración entre servicios;
- estándares QA;
- estándares de seguridad;
- CI/CD;
- despliegue;
- operación;
- troubleshooting.

## README por repositorio

Debe incluir:

- objetivo;
- responsabilidades;
- arquitectura;
- instalación;
- variables;
- endpoints;
- pruebas;
- despliegue;
- integraciones;
- decisiones propias del repositorio.

## Tareas

1. Revisar documentación actual.
2. Actualizar `README.md`.
3. Actualizar `PROJECT_CONTEXT.md`.
4. Crear documentación técnica base.
5. Crear repositorios en Azure Repos.
6. Definir si se usará mirror o migración.
7. Crear Boards por producto o dominio.
8. Crear Wiki central.
9. Enlazar work items con commits y PR.
10. Mantener GitHub como portafolio público.

## Resultado esperado

- documentación distribuida correctamente;
- repositorios documentados;
- Notion reducido a visión y roadmap;
- Azure DevOps como centro operativo.

---

# 8. Fase 5 — Integración inicial de `sbm-ai-assistant`

## Objetivo

Transformar el asistente desde un lector RAG hacia un orquestador de herramientas, APIs, agentes y canales de comunicación.

## Orden de implementación

### 1. SBM API Integration Agent

- detectar intención;
- decidir entre `sbm-api` y `dp-api`;
- ejecutar tools controladas;
- comenzar con operaciones de lectura;
- validar permisos y marca;
- registrar ejecución;
- solicitar confirmación para escritura.

### 2. Azure Boards Agent

- crear y consultar backlog técnico;
- generar bugs, tareas y Product Backlog Items;
- crear criterios de aceptación;
- actualizar estados;
- relacionar trabajo con commits, pull requests y pipelines.

### 3. Notion Documentation Agent

- leer y actualizar páginas autorizadas;
- mantener roadmap;
- registrar decisiones;
- generar resúmenes;
- solicitar aprobación para cambios importantes.

### 4. Jira Business Agent

- gestionar tareas operativas;
- registrar requerimientos comerciales;
- campañas;
- solicitudes internas;
- procesos de negocio.

### 5. OpenClaw Multichannel Gateway

OpenClaw se evaluará como una integración opcional para exponer `sbm-ai-assistant` en múltiples canales sin desarrollar cada conector desde cero.

Canales potenciales:

- Slack;
- WhatsApp;
- Telegram;
- Microsoft Teams;
- otros canales compatibles.

Responsabilidades:

- recibir mensajes desde distintos canales;
- conservar contexto de sesión cuando corresponda;
- redirigir solicitudes hacia `sbm-ai-assistant`;
- unificar la entrada multicanal;
- aplicar autenticación y permisos mínimos;
- evitar acceso directo a `sbm-api`, `dp-api`, bases de datos o infraestructura crítica.

OpenClaw no reemplazará:

- `sbm-ai-assistant`;
- el Intent Router;
- el Tool Router;
- LangGraph;
- MCP;
- la capa de permisos;
- la aprobación humana.

Estado:

- Research;
- Optional;
- posterior a las integraciones prioritarias.

## Componentes técnicos

- Intent Router;
- Tool Router;
- Agent Orchestrator;
- API Clients;
- MCP Clients;
- Permission and Policy Layer;
- Human Approval;
- Audit and Observability;
- Multichannel Gateway opcional.

## Arquitectura objetivo

```
Slack / WhatsApp / Telegram / Teams
                │
                ▼
     OpenClaw — opcional
                │
                ▼
       sbm-ai-assistant
                │
                ├── Intent Router
                ├── Tool Router
                ├── Agent Orchestrator
                ├── RAG
                ├── API Clients
                ├── MCP Clients
                ├── Permission Layer
                └── Human Approval
```

## Resultado esperado

- consultas conversacionales sobre datos reales;
- backlog técnico gestionable por chat;
- actualización controlada de Notion;
- Jira separado para tareas de negocio;
- prueba de concepto multicanal mediante OpenClaw;
- `sbm-ai-assistant` mantenido como orquestador central.

---

# 9. Fase 6 — Redis, Celery y scheduling

## Objetivo

Incorporar procesamiento asíncrono y tareas programadas.

## Redis

Usos:

- broker;
- caché;
- locks;
- datos temporales;
- control de concurrencia.

## Celery

Usos:

- tareas pesadas;
- reintentos;
- generación documental;
- sincronizaciones;
- correos;
- IA;
- integraciones externas.

## Celery Beat

Usos:

- tareas periódicas;
- sincronización de Confluence;
- procesos programados;
- actualizaciones diarias;
- mantenimiento.

## Tareas

1. Crear infraestructura Redis.
2. Configurar workers por servicio.
3. Configurar Celery Beat.
4. Incorporar Flower.
5. Migrar el scheduler de `sbm-ai-assistant`.
6. Definir políticas de retry.
7. Definir idempotencia.
8. Implementar dead-letter handling cuando corresponda.
9. Incorporar métricas y logs.

## Resultado esperado

- procesamiento asíncrono estable;
- scheduler desacoplado;
- tareas observables;
- soporte para múltiples réplicas.

---

# 10. Fase 7 — Kafka y arquitectura event-driven

## Objetivo

Desacoplar procesos entre servicios mediante eventos empresariales.

## Infraestructura

- Kafka con KRaft;
- Kafka UI;
- Schema Registry;
- AsyncAPI;
- Strimzi como investigación futura para Kubernetes.

## Eventos iniciales potenciales

```
product.created
product.updated
material.updated
order.created
inventory.updated
price.changed
document.approved
appointment.scheduled
campaign.created
invoice.issued
```

## Tareas

1. Definir catálogo de eventos.
2. Definir esquemas.
3. Incorporar Outbox Pattern.
4. Crear productores.
5. Crear consumidores.
6. Definir idempotencia.
7. Definir retries y errores.
8. Documentar eventos con AsyncAPI.
9. Implementar observabilidad.
10. Evitar que Kafka reemplace indebidamente a Celery.

## Resultado esperado

- integración desacoplada;
- trazabilidad de eventos;
- base para omnicanalidad y agentes.

---

# 11. Fase 8 — Kubernetes y Platform Engineering

## Objetivo

Desplegar SBM Suite localmente en una arquitectura Kubernetes demostrable.

## Tecnologías

- Kubernetes;
- K3s;
- k3d;
- Helm;
- Ingress NGINX;
- cert-manager;
- ConfigMaps;
- Secrets;
- RBAC;
- Network Policies;
- probes;
- autoscaling;
- persistent volumes.

## Tareas

1. Crear clúster k3d.
2. Definir namespaces.
3. Crear charts Helm.
4. Migrar servicios gradualmente.
5. Configurar ingress.
6. Configurar certificados.
7. Configurar secrets.
8. Incorporar liveness y readiness.
9. Configurar recursos y límites.
10. Agregar autoscaling donde tenga sentido.
11. Mantener PostgreSQL fuera del clúster inicialmente.
12. Integrar despliegue con Jenkins y Azure Pipelines.

## Resultado esperado

- despliegue reproducible;
- arquitectura de plataforma demostrable;
- charts versionados;
- evidencia de Kubernetes real.

---

# 12. Fase 9 — Observabilidad y monitoreo

## Objetivo

Observar la plataforma completa desde aplicaciones hasta agentes IA.

## Tecnologías

- OpenTelemetry;
- Prometheus;
- Grafana;
- Loki;
- Tempo;
- Alertmanager;
- structured logging;
- correlation IDs;
- Kafka UI;
- Flower;
- Langfuse Self-Hosted.

## Tareas

1. Definir estándar de logs.
2. Implementar correlation IDs.
3. Exponer métricas.
4. Instrumentar trazas.
5. Crear dashboards.
6. Crear alertas.
7. Monitorear Celery.
8. Monitorear Kafka.
9. Monitorear bases de datos.
10. Incorporar health checks.
11. Incorporar observabilidad LLM.
12. Medir tokens, latencia, costo y errores.

## Resultado esperado

- trazabilidad extremo a extremo;
- dashboards técnicos;
- alertas;
- evidencia visible para el portafolio.

---

# 13. Fase 10 — `ks-store` y configuración digital por marca

## Objetivo

Publicar la primera tienda de marca y crear la base reusable para futuros canales.

## Tareas

1. Definir configuración digital de marca.
2. Crear estructura de datos para:
    - dominio;
    - correo;
    - teléfono;
    - WhatsApp;
    - redes sociales;
    - logo;
    - imágenes;
    - datos legales;
    - SEO;
    - canales activos.
3. Conectar la tienda con `dp-api`.
4. Implementar catálogo.
5. Implementar productos.
6. Implementar imágenes y videos.
7. Implementar contacto y WhatsApp.
8. Implementar SEO.
9. Implementar analítica.
10. Implementar pruebas y seguridad.

## Resultado esperado

- primera tienda pública;
- configuración reutilizable por marca;
- base para canales digitales futuros.

---

# 14. Fase 11 — `sbm-digital-api` y canales públicos

## Objetivo

Crear una capa Node.js/NestJS justificada como BFF y Digital Experience API.

## Responsabilidades

- agregación de APIs;
- composición de respuestas;
- autenticación pública;
- rate limiting;
- caché;
- WebSockets;
- Server-Sent Events;
- SEO;
- multimedia;
- redes sociales;
- marketplaces;
- aislamiento de APIs internas.

## Consumidores

- `sbm-comercial`;
- `ks-store`;
- futuras tiendas;
- aplicaciones móviles;
- redes sociales;
- marketplaces.

## Resultado esperado

- canales públicos desacoplados;
- uso real de Node.js/NestJS;
- soporte omnicanal.

---

# 15. Fase 12 — Comercio omnicanal y marketplaces

## Objetivo

Centralizar ventas, stock, precios y pedidos en múltiples canales.

## Mercado Libre

Tareas:

- autenticación;
- publicaciones;
- productos;
- stock;
- precios;
- pedidos;
- preguntas;
- despachos;
- comisiones;
- reputación;
- conciliación.

## Tipo de cambio

Para negocios de importación:

1. consultar USD diario;
2. guardar historial;
3. registrar fuente;
4. calcular costos;
5. incorporar transporte, aranceles e IVA;
6. calcular márgenes;
7. generar precios sugeridos;
8. solicitar aprobación;
9. sincronizar canales.

## Resultado esperado

- gestión omnicanal;
- caso real para Kiseki Tech;
- precios y stock centralizados.

---

# 16. Fase 13 — Machine Learning y Deep Learning

## Objetivo

Incorporar modelos solo cuando exista un caso de negocio concreto.

## Casos potenciales

- predicción de demanda;
- forecasting de ventas;
- optimización de inventario;
- precios sugeridos;
- anomalías;
- segmentación;
- recomendaciones;
- OCR;
- clasificación documental;
- análisis de campañas;
- forecasting financiero.

## Etapas

1. definición del problema;
2. recopilación de datos;
3. calidad de datos;
4. baseline;
5. experimentación;
6. evaluación;
7. versionado;
8. despliegue;
9. monitoreo;
10. retraining.

## Resultado esperado

- modelos ligados a procesos reales;
- evidencia de ML aplicada;
- MLOps progresivo.

---

# 17. Fase 14 — Agentes especializados

## Objetivo

Ampliar `sbm-ai-assistant` como orquestador de una fuerza de trabajo digital controlada.

## Agentes futuros

- Executive Assistant Agent;
- Finance Agent;
- Accounting Agent;
- Marketing Agent;
- Content Agent;
- Social Media Agent;
- Sales Agent;
- Customer Service Agent;
- Inventory Agent;
- Procurement Agent;
- Operations Agent;
- Franchise Agent;
- Legal and Compliance Agent;
- Tax Integration Agent;
- Marketplace Agent;
- Scheduling Agent;
- HR Agent;
- Analytics Agent;
- Security Agent;
- QA Agent;
- DevOps Agent.

## Controles obligatorios

- tools autorizadas;
- permisos mínimos;
- acceso por marca;
- auditoría;
- validación;
- límites;
- aprobación humana;
- trazabilidad;
- manejo de errores;
- políticas de seguridad.

## Resultado esperado

- automatización empresarial progresiva;
- agentes especializados;
- control humano sobre decisiones críticas.

---

# 18. Fase 15 — Marketing y Content Factory

## Objetivo

Automatizar planificación, generación, aprobación y publicación de contenido.

## Flujo

```
Datos de productos y campañas
            ↓
Agentes IA
            ↓
Briefs, copys, guiones y prompts
            ↓
Figma / ComfyUI / Adobe / Blender
            ↓
Cloudinary
            ↓
Redes sociales, tiendas y campañas
```

## Herramientas

- Figma;
- Figma API;
- Photoshop;
- Illustrator;
- Premiere Pro;
- After Effects;
- Blender;
- DaVinci Resolve;
- ComfyUI;
- Cloudinary;
- YouTube;
- n8n;
- APIs oficiales de redes sociales.

## Resultado esperado

- fábrica de contenido asistida por IA;
- publicación controlada;
- activos reutilizables;
- métricas de campañas.

---

# 19. Fase 16 — Operaciones y planificación visual

## Objetivo

Crear un módulo visual para locales, espacios, equipamiento, permisos y planos.

## Alcance

- drag-and-drop;
- bloques;
- capas;
- medidas;
- zonas;
- historial;
- comentarios;
- versiones;
- aprobaciones;
- exportación.

## Tecnologías potenciales

- Vue Flow;
- React Flow;
- Konva.js;
- Fabric.js;
- Three.js;
- SVG;
- DXF;
- Blender;
- Figma.

## Resultado esperado

- editor operativo visual;
- gestión de planos y permisos;
- aplicación real para Ditaly Pasta y Consorcio Gastronómico.

---

# 20. Fase 17 — Finanzas

## Objetivo

Centralizar la gestión financiera de las marcas.

## Funciones

- flujo de caja;
- ingresos;
- egresos;
- cuentas por cobrar;
- cuentas por pagar;
- presupuestos;
- centros de costo;
- conciliación;
- proyecciones;
- rentabilidad;
- alertas;
- dashboards;
- análisis por marca y sucursal.

## Resultado esperado

- control financiero centralizado;
- datos preparados para agentes y modelos predictivos.

---

# 21. Fase 18 — Contabilidad e integración tributaria

## Objetivo

Incorporar contabilidad sin acoplar SBM Suite directamente a los cambios técnicos del SII.

## Arquitectura

```
SBM Suite
    ↓
Accounting / Billing Module
    ↓
DTE Provider Adapter
    ↓
Proveedor externo de facturación
    ↓
SII
```

## Funciones

- facturas;
- boletas;
- notas de crédito;
- notas de débito;
- guías de despacho;
- estados;
- rechazos;
- acuses;
- conciliación;
- auditoría.

## Principio

El proveedor externo debe absorber cambios estructurales del SII, mientras SBM Suite mantiene una interfaz interna estable.

## Resultado esperado

- integración tributaria desacoplada;
- proveedor reemplazable;
- menor riesgo operativo.

---

# 22. Fase 19 — Empresa autónoma supervisada

## Objetivo

Consolidar SBM Suite como un sistema operativo empresarial inteligente.

## Modelo

```
Human Leadership
        +
AI Agent Workforce
        +
SBM Suite
        +
Internal API
        +
Brand Client APIs
        +
Digital Channels
        +
Automation
        +
Analytics
```

## Principios

- estructura humana reducida;
- automatización amplia;
- decisiones críticas supervisadas;
- permisos mínimos;
- trazabilidad;
- control por marca;
- auditoría;
- mejora continua.

---

# 23. Priorización consolidada

## Urgente

1. AI-3016 y preparación Azure.
2. Separación `sbm-api` / `dp-api`.
3. Estabilización de `product` y `material`.
4. QA transversal.
5. SonarQube y cobertura.
6. Seguridad DevSecOps.
7. Documentación por repositorio.
8. Azure DevOps.
9. Integración de `sbm-ai-assistant` con APIs.

## Corto plazo

1. Azure Boards Agent.
2. Notion Documentation Agent.
3. Jira Business Agent.
4. Redis.
5. Celery.
6. Celery Beat.
7. Kafka.
8. Kubernetes.
9. Observabilidad.

## Mediano plazo

1. `ks-store`.
2. configuración digital por marca;
3. `sbm-digital-api`;
4. comercio omnicanal;
5. Mercado Libre;
6. SEO;
7. multimedia;
8. Machine Learning;
9. agentes especializados.

## Largo plazo

1. marketing;
2. Content Factory;
3. operaciones y planos;
4. finanzas;
5. contabilidad;
6. integración tributaria;
7. mayor autonomía empresarial.

---

# 24. Criterio de finalización por fase

Una fase se considera completada cuando:

1. la implementación funciona;
2. tiene pruebas;
3. supera Quality Gate;
4. tiene escaneo de seguridad;
5. está documentada;
6. tiene observabilidad cuando corresponda;
7. puede demostrarse;
8. genera evidencia para el portafolio;
9. no deja dependencias críticas ocultas;
10. su operación y mantenimiento están claros.

---

# 25. Production-brand implementation track — 2026-08-16

Immediate architecture track:

1. stabilize DP as reusable historical reference;
2. complete shared data/model objectives in SBM-DB without assuming unimplemented schema changes;
3. create `ks-api`, `pc-api`, `cg-api`;
4. create `sbm-core`, `sbm-calculation`, `sbm-util`;
5. create required stores/mobile/client channels;
6. create control planes and specialized agents;
7. harden production topology, storage, security and observability.

Kiseki rental/contracts/technical service/spares remain long-term and must not block the immediate sale/import scope.

---

## Legacy digital roadmap concepts

`sbm-comercial` and `sbm-digital-api` remain historical roadmap concepts, not current approved project-creation objectives. The current target favors direct brand APIs plus brand stores/client/mobile channels. Reactivate a transversal commercial portal/BFF only if a concrete cross-brand requirement justifies it.
