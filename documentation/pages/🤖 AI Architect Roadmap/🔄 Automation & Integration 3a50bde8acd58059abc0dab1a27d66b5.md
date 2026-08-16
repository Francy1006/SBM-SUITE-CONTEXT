# 🔄 Automation & Integration

> Estrategia transversal de automatización e integración para SBM Suite.
> 
> 
> Esta página define cómo conectar aplicaciones, APIs, servicios externos, flujos de negocio, agentes IA y procesos internos mediante integraciones seguras, trazables y mantenibles.
> 
> El objetivo es reducir trabajo manual, evitar duplicaciones, desacoplar sistemas y transformar SBM Suite en una plataforma operativa capaz de coordinar procesos empresariales de extremo a extremo.
> 

---

# 1. Objetivo

Construir una capa de automatización e integración que permita:

- conectar servicios internos;
- conectar APIs externas;
- automatizar procesos repetitivos;
- orquestar tareas;
- integrar agentes IA;
- coordinar herramientas empresariales;
- desacoplar sistemas;
- soportar flujos síncronos y asíncronos;
- centralizar auditoría;
- controlar errores y reintentos;
- generar evidencia técnica para el portafolio.

---

# 2. Alcance

La estrategia cubre:

- `sbm-api`;
- `dp-api`;
- `sbm-ai-assistant`;
- `sbm-manager`;
- `sbm-comercial`;
- `sbm-digital-api`;
- `ks-store`;
- Azure DevOps;
- Jira;
- Notion;
- Confluence;
- Slack;
- WhatsApp;
- Microsoft Teams;
- Telegram;
- Mercado Libre;
- facturación electrónica;
- Banco Central de Chile;
- Google APIs;
- redes sociales;
- n8n;
- Redis;
- Celery;
- Kafka;
- MCP;
- webhooks;
- agentes IA.

---

# 3. Principios

1. **API-first**
    
    Las integraciones deben utilizar contratos explícitos.
    
2. **Loose coupling**
    
    Los sistemas no deben depender innecesariamente de detalles internos.
    
3. **Asynchronous when appropriate**
    
    Los procesos lentos o desacoplados deben ejecutarse de forma asíncrona.
    
4. **Idempotency**
    
    Repetir una operación no debe producir efectos duplicados.
    
5. **Observability**
    
    Cada integración debe registrar estado, duración, errores y resultado.
    
6. **Security by design**
    
    Autenticación, permisos y secretos deben gestionarse desde el inicio.
    
7. **Retry with control**
    
    Los reintentos deben tener límites y backoff.
    
8. **Human approval**
    
    Las operaciones críticas deben requerir confirmación.
    
9. **Canonical contracts**
    
    Los datos compartidos deben tener schemas estables.
    
10. **Portfolio relevance**
    
    Las integraciones deben demostrar problemas reales resueltos.
    

---

# 4. Arquitectura objetivo

```
Channels and External Systems
            │
            ▼
Integration Layer
            │
            ├── REST APIs
            ├── Webhooks
            ├── MCP
            ├── n8n
            ├── Celery
            ├── Kafka
            └── Agent Tools
            │
            ▼
SBM Services
            │
            ├── sbm-api
            ├── dp-api
            ├── sbm-digital-api
            ├── sbm-ai-assistant
            └── Future Client APIs
```

---

# 5. Tipos de integración

| Tipo | Uso |
| --- | --- |
| REST API | Comunicación síncrona |
| Webhook | Notificaciones externas |
| Queue | Trabajo asíncrono |
| Event Streaming | Eventos entre servicios |
| MCP | Tools y recursos para agentes |
| Workflow Automation | Flujos de negocio |
| File Exchange | Documentos o lotes |
| Scheduled Jobs | Procesos periódicos |
| Direct Database Access | Evitar salvo casos muy controlados |

---

# 6. Integración entre `sbm-api` y `dp-api`

## Objetivo

Separar responsabilidades sin perder coordinación entre servicios.

## Principio

- `sbm-api`: procesos internos y transversales;
- `dp-api`: API cliente de Ditaly Pasta;
- no compartir lógica de negocio mediante duplicación;
- no escribir directamente en bases ajenas;
- integrar mediante contratos claros.

## Flujos iniciales

### Lectura

```
sbm-manager
    ↓
dp-api
    ↓
Consulta autorizada
    ↓
Respuesta
```

### Operación asíncrona

```
dp-api
   ↓
Task or Event
   ↓
sbm-api
   ↓
Process
   ↓
Result or Event
```

## Controles

- autenticación servicio a servicio;
- idempotency key;
- correlation ID;
- schemas;
- retries;
- timeout;
- auditoría;
- validación por marca.

---

# 7. n8n

## Rol

n8n será la plataforma principal de automatización visual.

## Casos

- Slack;
- Jira;
- Azure Boards;
- Notion;
- Confluence;
- correo;
- APIs externas;
- notificaciones;
- aprobaciones;
- campañas;
- sincronizaciones;
- tareas programadas;
- flujos de agentes.

## Principio

n8n no debe contener lógica crítica que pertenezca a una API de negocio.

## Debe utilizarse para

- orquestación;
- integración;
- transformación ligera;
- notificaciones;
- coordinación;
- procesos administrativos.

## No debe utilizarse para

- reglas complejas;
- cálculos críticos;
- transacciones sensibles;
- persistencia principal;
- autorización central.

---

# 8. Redis y Celery

## Rol

Procesamiento asíncrono y tareas en segundo plano.

## Casos

- sincronización documental;
- generación de embeddings;
- envío de correos;
- importaciones;
- exportaciones;
- notificaciones;
- llamadas a APIs lentas;
- retries;
- tareas de agentes;
- procesamiento de archivos;
- actualización de datos externos.

## Flujo

```
API
 ↓
Celery Task
 ↓
Redis Broker
 ↓
Worker
 ↓
External System
 ↓
Result
```

## Requisitos

- idempotencia;
- retry policy;
- timeout;
- dead-letter handling;
- observabilidad;
- tracing;
- alertas.

---

# 9. Celery Beat

## Rol

Scheduling distribuido.

## Casos

- sincronización Confluence;
- actualización de indicadores;
- tipo de cambio diario;
- mantenimiento de índices;
- reportes;
- tareas de limpieza;
- evaluaciones IA;
- recordatorios;
- campañas programadas.

## Principio

Reemplazar progresivamente schedulers embebidos cuando exista más de una réplica.

---

# 10. Kafka

## Rol

Arquitectura event-driven para eventos de negocio.

## Eventos iniciales

```
product.created
product.updated
material.updated
order.created
inventory.updated
price.changed
document.approved
campaign.created
invoice.issued
appointment.scheduled
```

## Casos

- desacoplar servicios;
- sincronizar datos;
- activar procesos;
- generar notificaciones;
- alimentar analítica;
- coordinar agentes;
- registrar auditoría.

## Requisitos

- schemas;
- versionado;
- idempotencia;
- consumer groups;
- retries;
- dead-letter topics;
- observabilidad;
- AsyncAPI.

---

# 11. Webhooks

## Casos

- Slack;
- Mercado Libre;
- proveedores externos;
- facturación electrónica;
- pagos;
- redes sociales;
- Azure DevOps;
- Jira;
- Notion.

## Controles

- firma;
- timestamp;
- replay protection;
- idempotencia;
- rate limiting;
- logging;
- validación;
- cola asíncrona;
- respuesta rápida.

---

# 12. Model Context Protocol

## Rol

Conectar agentes con herramientas y recursos de manera estandarizada.

## Casos

- Notion;
- Obsidian;
- documentación;
- Azure DevOps;
- herramientas internas;
- recursos empresariales;
- servidores de conocimiento.

## Controles

- servidores autorizados;
- autenticación;
- allowlist de tools;
- permisos;
- logs;
- límites;
- revisión de recursos.

---

# 13. OpenClaw

## Rol

Gateway multicanal opcional para `sbm-ai-assistant`.

## Canales potenciales

- Slack;
- WhatsApp;
- Telegram;
- Microsoft Teams.

## Arquitectura

```
Channels
   ↓
OpenClaw
   ↓
sbm-ai-assistant
   ↓
Tools / APIs / MCP / Agents
```

## Principios

- no reemplaza `sbm-ai-assistant`;
- no accede directamente a bases de datos;
- no controla infraestructura;
- solo consume capacidades autorizadas;
- debe aplicar permisos mínimos.

## Estado

- Research;
- Optional;
- posterior a integraciones prioritarias.

---

# 14. Slack

## Estado actual

Slack ya funciona como interfaz principal de `sbm-ai-assistant`.

## Casos

- consultas RAG;
- consultas a APIs;
- creación de tareas;
- seguimiento;
- alertas;
- aprobaciones;
- comandos operativos.

## Controles

- firma;
- canal autorizado;
- threads;
- deduplicación;
- permisos;
- auditoría;
- manejo de retries.

---

# 15. Azure Boards

## Rol

Backlog técnico oficial.

## Integraciones

- API REST;
- webhooks;
- agente IA;
- pipelines;
- repositorios;
- pull requests;
- dashboards.

## Casos

- crear PBI;
- crear bug;
- crear task;
- actualizar estados;
- agregar criterios de aceptación;
- vincular commits;
- generar reportes.

---

# 16. Jira

## Rol

Gestión de tareas de negocio y operación.

## Casos

- solicitudes comerciales;
- campañas;
- operaciones;
- requerimientos internos;
- tareas de clientes;
- procesos administrativos.

## Integración

- Jira API;
- n8n;
- `sbm-ai-assistant`;
- webhooks.

---

# 17. Notion

## Rol

Visión, roadmap y documentación general.

## Casos

- lectura de páginas;
- actualización de estados;
- creación de secciones;
- resúmenes;
- decisiones;
- seguimiento.

## Integraciones

- Notion API;
- MCP;
- agente documental;
- n8n.

---

# 18. Confluence

## Estado actual

Fuente documental conectada a `sbm-ai-assistant`.

## Casos

- ingestión;
- sincronización;
- versionado;
- RAG;
- recuperación de conocimiento;
- actualización programada.

## Evolución

- integración con Celery Beat;
- trazabilidad;
- filtros;
- evaluación;
- seguridad documental.

---

# 19. Mercado Libre

## Objetivo

Integrar publicaciones, precios, stock y pedidos.

## Flujos

- importar publicaciones;
- sincronizar stock;
- actualizar precios;
- recibir pedidos;
- responder preguntas;
- consultar comisiones;
- conciliación;
- reputación.

## Controles

- rate limits;
- tokens;
- retries;
- webhooks;
- idempotencia;
- logs;
- aprobación para cambios sensibles.

---

# 20. Tipo de cambio

## Fuente

Fuente oficial del Banco Central de Chile.

## Flujo

```
Scheduled Job
   ↓
Official Source
   ↓
Validation
   ↓
Store Historical Rate
   ↓
Cost Calculation
   ↓
Suggested Price
   ↓
Human Approval
```

## Casos

- Kiseki Tech;
- importaciones;
- márgenes;
- precios;
- proyecciones.

---

# 21. Facturación electrónica

## Arquitectura

```
SBM Suite
   ↓
Billing Module
   ↓
DTE Provider Adapter
   ↓
External Provider
   ↓
SII
```

## Principio

No integrar directamente toda la complejidad del SII en el núcleo.

## Casos

- facturas;
- boletas;
- notas de crédito;
- notas de débito;
- guías;
- estados;
- rechazos;
- acuses;
- conciliación.

---

# 22. Google APIs

## Casos

- Calendar;
- Gmail;
- Drive;
- Sheets;
- Maps;
- Analytics;
- Search Console;
- Tag Manager.

## Uso futuro

- agenda;
- notificaciones;
- documentos;
- reporting;
- ubicaciones;
- analítica;
- SEO.

---

# 23. Social Media APIs

## Integraciones

- Meta Graph API;
- Instagram Graph API;
- YouTube Data API;
- LinkedIn API;
- TikTok API;
- WhatsApp Business Platform.

## Casos

- publicar;
- programar;
- consultar métricas;
- responder;
- sincronizar contenido;
- campañas;
- atención.

---

# 24. Email

## Casos

- notificaciones;
- alertas;
- reportes;
- confirmaciones;
- aprobaciones;
- campañas;
- recuperación de cuenta.

## Requisitos

- templates;
- colas;
- retries;
- tracking controlado;
- logs;
- evitar exposición de datos.

---

# 25. Calendar and Scheduling

## Casos

- agenda;
- citas;
- operativos;
- reuniones;
- recordatorios;
- reservas;
- disponibilidad.

## Integraciones

- Google Calendar;
- Microsoft Calendar;
- APIs internas;
- agentes;
- n8n.

---

# 26. Authentication between Services

## Opciones

- OAuth 2.0;
- client credentials;
- signed tokens;
- API keys limitadas;
- mutual TLS como opción futura.

## Requisitos

- expiración;
- rotación;
- scopes;
- auditoría;
- secretos seguros;
- revocación.

---

# 27. Canonical Data Models

## Objetivo

Evitar conversiones inconsistentes entre servicios.

## Entidades iniciales

- brand;
- user;
- product;
- material;
- price;
- order;
- customer;
- branch;
- provider;
- document;
- task;
- event.

## Requisitos

- schemas;
- versionado;
- naming;
- IDs;
- timestamps;
- metadata;
- source system.

---

# 28. API Contracts

## Herramientas

- OpenAPI;
- JSON Schema;
- AsyncAPI;
- Pact;
- Schemathesis.

## Reglas

- contratos versionados;
- breaking changes controlados;
- deprecación;
- pruebas automáticas;
- documentación;
- ejemplos.

---

# 29. Idempotency

## Casos

- creación de pedidos;
- webhooks;
- pagos;
- publicación;
- facturación;
- eventos;
- tareas asíncronas.

## Estrategia

- idempotency key;
- almacenamiento temporal;
- validación de duplicados;
- respuesta consistente;
- expiración.

---

# 30. Retry Strategy

## Tipos

- retry inmediato;
- exponential backoff;
- retry programado;
- dead-letter queue;
- manual retry.

## Regla

No reintentar errores funcionales permanentes.

---

# 31. Circuit Breaker

## Objetivo

Evitar saturar dependencias fallidas.

## Estados

- closed;
- open;
- half-open.

## Casos

- proveedores externos;
- LLM;
- Mercado Libre;
- facturación;
- Google APIs;
- redes sociales.

---

# 32. Error Handling

## Estructura mínima

```
Integration Error
├── source
├── destination
├── operation
├── timestamp
├── trace ID
├── retry count
├── status
├── payload reference
└── error detail
```

## Reglas

- no perder errores;
- no exponer secretos;
- registrar contexto;
- clasificar;
- alertar cuando corresponda;
- permitir reintento manual.

---

# 33. Dead-Letter Handling

## Casos

- Celery tasks fallidas;
- eventos Kafka;
- webhooks;
- integraciones externas;
- mensajes inválidos.

## Acciones

- almacenar;
- alertar;
- analizar;
- corregir;
- reintentar;
- cerrar con auditoría.

---

# 34. Human Approval

## Operaciones

- precios;
- pagos;
- facturación;
- publicación;
- campañas;
- cambios masivos;
- permisos;
- infraestructura;
- documentos críticos.

## Flujo

```
Request
  ↓
Validation
  ↓
Draft
  ↓
Human Approval
  ↓
Execution
  ↓
Audit
```

---

# 35. Observability

Cada integración debe medir:

- requests;
- éxito;
- error;
- latencia;
- retries;
- timeouts;
- payload size;
- provider;
- cost;
- trace ID;
- actor;
- brand.

---

# 36. Security

## Controles

- OAuth;
- scopes;
- secrets management;
- rate limiting;
- input validation;
- signature validation;
- encryption;
- audit;
- IP restrictions cuando corresponda;
- least privilege.

---

# 37. Testing

## Tipos

- unit;
- integration;
- contract;
- end-to-end;
- webhook;
- resilience;
- performance;
- security.

## Casos

- API caída;
- timeout;
- respuesta inválida;
- mensaje duplicado;
- reintento;
- acceso no autorizado;
- evento fuera de orden;
- operación parcial.

---

# 38. Automation Governance

## Cada flujo debe definir

- owner;
- objetivo;
- trigger;
- inputs;
- outputs;
- permisos;
- dependencia;
- retry;
- timeout;
- observabilidad;
- rollback;
- documentación.

---

# 39. Roadmap de implementación

## Etapa 1 — Integración interna

1. inventariar APIs;
2. definir contratos;
3. conectar `sbm-ai-assistant`;
4. implementar autenticación servicio a servicio;
5. agregar correlation IDs;
6. agregar idempotencia.

## Etapa 2 — Automatización

1. estabilizar n8n;
2. Redis;
3. Celery;
4. Celery Beat;
5. Flower;
6. retries;
7. dead-letter handling.

## Etapa 3 — Herramientas empresariales

1. Azure Boards;
2. Notion;
3. Jira;
4. Slack;
5. Confluence;
6. Gmail y Calendar.

## Etapa 4 — Event-Driven

1. catálogo de eventos;
2. Kafka;
3. Schema Registry;
4. AsyncAPI;
5. consumidores;
6. observabilidad.

## Etapa 5 — Canales y comercio

1. OpenClaw;
2. WhatsApp;
3. Teams;
4. Mercado Libre;
5. social media;
6. facturación electrónica.

---

# 40. Prioridad actual

## Urgente

1. contratos entre `sbm-api` y `dp-api`;
2. integración de `sbm-ai-assistant`;
3. autenticación;
4. idempotencia;
5. correlation IDs;
6. Azure Boards;
7. Notion;
8. Jira.

## Corto plazo

1. Redis;
2. Celery;
3. Celery Beat;
4. Flower;
5. webhooks;
6. Google APIs.

## Mediano plazo

1. Kafka;
2. AsyncAPI;
3. OpenClaw;
4. Mercado Libre;
5. redes sociales;
6. facturación.

---

# 41. Evidencia para portafolio

## Entregables

- diagramas de integración;
- contratos OpenAPI;
- AsyncAPI;
- workflows n8n;
- agentes conectados;
- trazas;
- reportes;
- retries;
- dead-letter examples;
- webhooks validados;
- demo multicanal;
- video técnico.

---

# 42. Criterio de finalización

Una integración se considera completada cuando:

1. tiene contrato;
2. tiene autenticación;
3. tiene validación;
4. tiene idempotencia cuando corresponde;
5. tiene retry;
6. tiene timeout;
7. tiene observabilidad;
8. tiene pruebas;
9. tiene documentación;
10. tiene manejo de errores;
11. tiene seguridad;
12. puede demostrarse.

---

# 43. Visión final

```
APIs
 +
Events
 +
Workflows
 +
Agent Tools
 +
External Systems
 +
Human Approval
```

SBM Suite debe evolucionar hacia una plataforma conectada y automatizada, capaz de coordinar procesos internos, servicios externos y agentes IA con seguridad, trazabilidad y control.

---

# 44. sbm-core and sbm-util boundary — 2026-08-16

`sbm-core` owns cron/schedulers, durable flags/state, Celery workers, Redis, retries/idempotency and Kafka only when event-stream semantics justify it. `sbm-util` owns deterministic reusable integrations such as email, external APIs, file utilities and authoritative exchange-rate ingestion. Financial/accounting formulas belong to `sbm-calculation`, not `sbm-core`.
