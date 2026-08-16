# 📊 Observability & Monitoring

> Estrategia transversal de observabilidad para SBM Suite.
> 
> 
> Esta página define cómo medir, registrar, correlacionar y visualizar el comportamiento de aplicaciones, APIs, infraestructura, bases de datos, colas, eventos, agentes IA y modelos.
> 
> El objetivo es detectar problemas rápidamente, entender causas, medir rendimiento y operar la plataforma con evidencia real.
> 

---

# 1. Objetivo

Implementar observabilidad integral para:

- conocer el estado de cada servicio;
- detectar fallas;
- reducir tiempo de diagnóstico;
- medir rendimiento;
- correlacionar solicitudes entre servicios;
- monitorear infraestructura;
- visualizar métricas de negocio;
- monitorear agentes IA;
- medir tokens, latencia y costo;
- generar alertas;
- respaldar decisiones técnicas;
- demostrar operación profesional en el portafolio.

---

# 2. Alcance

La estrategia cubre:

- `SBM-MANAGER`;
- `SBM-API`;
- `DP-API`;
- `SBM-AI-ASSISTANT`;
- `SBM-DB`;
- `sbm-comercial`;
- `sbm-digital-api`;
- `KS-STORE`;
- PostgreSQL;
- Redis;
- Celery;
- Kafka;
- Qdrant;
- Docker;
- Kubernetes;
- NGINX;
- Jenkins;
- Azure DevOps;
- agentes IA;
- RAG;
- modelos ML;
- integraciones externas.

---

# 3. Principios

1. **Observability by default**
    
    Todo servicio debe emitir señales desde el inicio.
    
2. **Correlation first**
    
    Cada solicitud debe poder seguirse extremo a extremo.
    
3. **Structured data**
    
    Logs y eventos deben ser estructurados.
    
4. **Actionable alerts**
    
    Las alertas deben indicar una acción concreta.
    
5. **Business and technical visibility**
    
    Se deben observar métricas técnicas y de negocio.
    
6. **Low noise**
    
    Evitar alertas irrelevantes.
    
7. **Centralized visibility**
    
    Toda la plataforma debe visualizarse desde una capa común.
    
8. **Open standards**
    
    Priorizar OpenTelemetry.
    
9. **Self-hosted first**
    
    Priorizar herramientas gratuitas y locales.
    
10. **Evidence-oriented**
    
    Los dashboards y reportes deben servir como evidencia de portafolio.
    

---

# 4. Los cuatro pilares

| Pilar | Objetivo |
| --- | --- |
| Logs | Registrar eventos y errores |
| Metrics | Medir comportamiento |
| Traces | Seguir solicitudes distribuidas |
| Profiles | Analizar consumo interno cuando sea necesario |

---

# 5. Arquitectura objetivo

```
Applications and Infrastructure
          │
          ├── Logs
          ├── Metrics
          ├── Traces
          └── Events
          │
          ▼
OpenTelemetry Collector
          │
          ├── Prometheus
          ├── Loki
          ├── Tempo
          └── Langfuse
          │
          ▼
Grafana
          │
          ├── Dashboards
          ├── Alerts
          └── Investigation
```

---

# 6. Herramientas principales

| Tool | Uso |
| --- | --- |
| OpenTelemetry | Instrumentación estándar |
| OpenTelemetry Collector | Recolección y exportación |
| Prometheus | Métricas |
| Grafana | Dashboards |
| Loki | Logs |
| Tempo | Trazas |
| Alertmanager | Alertas |
| Grafana Alloy | Collector alternativo |
| Langfuse Self-Hosted | Observabilidad LLM |
| Flower | Monitoreo Celery |
| Kafka UI | Monitoreo Kafka |
| pg_stat_statements | Monitoreo PostgreSQL |

---

# 7. OpenTelemetry

## Objetivo

Estandarizar la instrumentación.

## Señales

- traces;
- metrics;
- logs;
- baggage;
- resource attributes.

## Atributos mínimos

- service name;
- service version;
- environment;
- request ID;
- trace ID;
- user ID anonimizado;
- brand ID;
- endpoint;
- status;
- duration;
- deployment version.

---

# 8. Correlation IDs

## Objetivo

Relacionar eventos entre servicios.

## Flujo

```
Frontend
   ↓
API Gateway
   ↓
SBM-API
   ↓
DP-API
   ↓
Celery
   ↓
Kafka
   ↓
External API
```

Todos deben conservar:

- `trace_id`;
- `span_id`;
- `request_id`;
- `correlation_id`.

---

# 9. Logs

## Requisitos

- JSON estructurado;
- timestamp;
- level;
- service;
- environment;
- trace ID;
- request ID;
- user;
- brand;
- event;
- message;
- duration;
- result;
- error type.

## Niveles

| Level | Uso |
| --- | --- |
| DEBUG | Diagnóstico local |
| INFO | Flujo normal |
| WARNING | Condición inesperada |
| ERROR | Fallo recuperable |
| CRITICAL | Fallo grave |

## Regla

No registrar:

- contraseñas;
- tokens;
- secretos;
- documentos sensibles completos;
- datos personales innecesarios.

---

# 10. Métricas de APIs

## Métricas

- requests por segundo;
- latencia p50;
- latencia p95;
- latencia p99;
- tasa de error;
- status codes;
- timeouts;
- retries;
- requests activas;
- payload size;
- dependency latency.

## Labels

- service;
- route;
- method;
- status;
- environment;
- brand cuando sea seguro.

---

# 11. Métricas de frontend

## Métricas

- Web Vitals;
- Largest Contentful Paint;
- Interaction to Next Paint;
- Cumulative Layout Shift;
- errores JavaScript;
- tiempo de carga;
- fallos de API;
- navegación;
- sesiones;
- rendimiento por ruta.

## Herramientas

- Lighthouse;
- PageSpeed Insights;
- browser telemetry;
- OpenTelemetry Web;
- Google Analytics para métricas de uso.

---

# 12. Métricas de PostgreSQL

## Métricas

- conexiones;
- queries lentas;
- locks;
- deadlocks;
- cache hit ratio;
- tamaño de tablas;
- tamaño de índices;
- replication lag futuro;
- transacciones;
- errores;
- tiempo de consulta.

## Herramientas

- PostgreSQL exporter;
- pg_stat_statements;
- Grafana dashboards;
- logs de PostgreSQL;
- EXPLAIN ANALYZE.

---

# 13. Métricas de Redis

## Métricas

- memoria;
- comandos;
- hits;
- misses;
- conexiones;
- evictions;
- latency;
- blocked clients;
- keyspace;
- replication futura.

## Herramientas

- Redis exporter;
- Prometheus;
- Grafana.

---

# 14. Celery Monitoring

## Herramientas

- Flower;
- Prometheus exporter;
- logs estructurados.

## Métricas

- tareas recibidas;
- tareas exitosas;
- tareas fallidas;
- tiempo de ejecución;
- retries;
- queue length;
- workers activos;
- tareas pendientes;
- timeouts;
- scheduled tasks.

---

# 15. Kafka Monitoring

## Herramientas

- Kafka UI;
- Prometheus exporters;
- Grafana;
- logs;
- OpenTelemetry.

## Métricas

- producer rate;
- consumer rate;
- consumer lag;
- partitions;
- broker health;
- under-replicated partitions;
- errors;
- retries;
- throughput;
- message size;
- dead-letter events.

---

# 16. Qdrant Monitoring

## Métricas

- collections;
- points;
- vector count;
- memory;
- search latency;
- indexing time;
- errors;
- payload filters;
- storage usage.

## Objetivo

Monitorear la salud y rendimiento del RAG.

---

# 17. NGINX Monitoring

## Métricas

- requests;
- status codes;
- latency;
- active connections;
- upstream errors;
- TLS errors;
- rate limiting;
- bandwidth;
- response size.

## Logs

- access logs;
- error logs;
- correlation IDs;
- upstream timing.

---

# 18. Docker Monitoring

## Métricas

- CPU;
- memory;
- network;
- disk;
- container restarts;
- health status;
- uptime.

## Herramientas

- cAdvisor;
- Prometheus;
- Grafana;
- Docker stats.

---

# 19. Kubernetes Monitoring

## Métricas

- pod status;
- restarts;
- CPU;
- memory;
- requests y limits;
- node status;
- deployments;
- replicas;
- HPA;
- pending pods;
- PVC;
- network;
- ingress.

## Herramientas

- kube-state-metrics;
- node exporter;
- Prometheus;
- Grafana;
- Loki;
- Tempo.

---

# 20. AI and LLM Observability

## Objetivo

Medir cada interacción de IA.

## Métricas

- input tokens;
- output tokens;
- total tokens;
- costo;
- modelo;
- proveedor;
- latencia;
- errores;
- retries;
- fallback;
- prompt version;
- tool selected;
- tool result;
- context retrieved;
- user feedback;
- quality score.

## Herramienta principal

Langfuse Self-Hosted.

---

# 21. RAG Observability

## Métricas

- query;
- retrieved chunks;
- source documents;
- relevance score;
- retrieval latency;
- reranking latency;
- answer latency;
- groundedness;
- citation coverage;
- no-answer rate;
- hallucination rate;
- access control failures.

---

# 22. Agent Observability

Cada ejecución debe registrar:

- agent name;
- intent;
- selected tool;
- input;
- output;
- risk level;
- approval status;
- retries;
- latency;
- result;
- error;
- actor;
- brand;
- trace ID.

## Casos a observar

- tool incorrecta;
- timeout;
- permisos insuficientes;
- operación parcial;
- retry excesivo;
- bucle de agente;
- uso de fallback;
- escalamiento humano.

---

# 23. Model Monitoring

## Métricas

- inference latency;
- prediction volume;
- error rate;
- input distribution;
- prediction distribution;
- data drift;
- model drift;
- accuracy real;
- confidence;
- version.

## Herramientas

- MLflow;
- Evidently AI;
- Prometheus;
- Grafana.

---

# 24. Business Metrics

## Objetivo

Relacionar salud técnica con impacto de negocio.

## Ejemplos

- ventas;
- pedidos;
- productos activos;
- quiebres de stock;
- tickets;
- conversiones;
- campañas;
- tiempos de atención;
- documentos procesados;
- tareas creadas por agentes;
- operaciones aprobadas;
- errores por marca.

---

# 25. Dashboards

## Dashboard ejecutivo

- salud general;
- disponibilidad;
- errores;
- ventas;
- alertas;
- agentes;
- costos IA.

## Dashboard de APIs

- latencia;
- errores;
- tráfico;
- dependencias;
- endpoints críticos.

## Dashboard de infraestructura

- CPU;
- memoria;
- disco;
- red;
- contenedores;
- pods.

## Dashboard IA

- tokens;
- costo;
- modelos;
- latencia;
- calidad;
- tools;
- errores.

## Dashboard de datos

- PostgreSQL;
- Redis;
- Kafka;
- Qdrant.

---

# 26. Alertas

## Principios

- accionables;
- con contexto;
- sin ruido;
- con severidad;
- con responsable;
- con enlace a dashboard;
- con runbook.

## Ejemplos

| Alerta | Condición |
| --- | --- |
| API unavailable | Health check fallido |
| High latency | p95 sobre umbral |
| Error spike | Incremento de 5xx |
| Database connections | Uso alto |
| Celery backlog | Cola creciente |
| Kafka lag | Lag fuera de rango |
| LLM errors | Fallos repetidos |
| Token cost | Consumo sobre presupuesto |
| Kubernetes restarts | Reinicios continuos |
| Disk usage | Espacio crítico |

---

# 27. Severidad

| Level | Significado |
| --- | --- |
| P1 | Caída crítica |
| P2 | Degradación severa |
| P3 | Problema importante |
| P4 | Advertencia |
| P5 | Informativo |

---

# 28. SLI, SLO and SLA

## SLI

Indicador medido:

- disponibilidad;
- latencia;
- error rate;
- throughput.

## SLO

Objetivo interno:

- 99.5% disponibilidad;
- p95 menor a umbral;
- error rate menor a 1%.

## SLA

Compromiso externo futuro.

## Principio

Comenzar con SLO internos antes de definir SLA formales.

---

# 29. Error Budgets

## Objetivo

Balancear confiabilidad y velocidad de cambio.

## Ejemplo

Si el SLO es 99.5%, el error budget permite una cantidad limitada de indisponibilidad.

Cuando se consume el presupuesto:

- reducir cambios;
- priorizar estabilidad;
- corregir causas;
- revisar arquitectura.

---

# 30. Health Checks

## Tipos

- liveness;
- readiness;
- startup;
- dependency health.

## Regla

Los health checks deben ser rápidos y no ejecutar operaciones costosas.

---

# 31. Synthetic Monitoring

## Casos

- login;
- consulta de producto;
- health endpoint;
- creación de pedido;
- consulta RAG;
- tool call;
- acceso a frontend.

## Herramientas

- k6;
- Playwright;
- scripts programados;
- Grafana Synthetic Monitoring como opción futura.

---

# 32. Incident Investigation

## Flujo

```
Alert
  ↓
Dashboard
  ↓
Trace
  ↓
Logs
  ↓
Metrics
  ↓
Root Cause
  ↓
Fix
  ↓
Postmortem
```

---

# 33. Runbooks

Cada alerta debe indicar:

- qué significa;
- cómo validar;
- dónde revisar;
- acciones inmediatas;
- rollback;
- escalamiento;
- responsable.

---

# 34. Postmortems

## Contenido

- resumen;
- impacto;
- línea de tiempo;
- causa raíz;
- factores contribuyentes;
- detección;
- respuesta;
- acciones correctivas;
- prevención.

## Principio

Sin culpas, centrado en mejorar el sistema.

---

# 35. Retention

## Logs

- corto plazo local;
- mediano plazo centralizado;
- mayor retención solo para auditoría.

## Métricas

- alta resolución reciente;
- agregación histórica.

## Trazas

- sampling;
- mayor retención para errores;
- menor retención para tráfico normal.

---

# 36. Sampling

## Estrategia

- 100% de errores;
- 100% de operaciones críticas;
- porcentaje reducido de solicitudes normales;
- sampling dinámico;
- sampling por servicio.

---

# 37. Cost Control

## Controles

- límites de retención;
- sampling;
- cardinalidad controlada;
- labels restringidos;
- compresión;
- dashboards útiles;
- evitar logs redundantes;
- alertas de costo.

## IA

- presupuesto por proveedor;
- tokens por usuario;
- tokens por agente;
- límite por flujo;
- fallback local.

---

# 38. Data Privacy

## Reglas

- anonimizar usuarios;
- no registrar secretos;
- no registrar payloads completos sensibles;
- controlar acceso;
- definir retención;
- separar datos por ambiente;
- auditar consultas.

---

# 39. CI/CD Observability

## Métricas

- duración de pipeline;
- tasa de éxito;
- fallas por etapa;
- tiempo de build;
- tiempo de test;
- tiempo de despliegue;
- rollback;
- frecuencia de releases.

## Herramientas

- Jenkins metrics;
- Azure DevOps dashboards;
- GitHub Actions metrics;
- Prometheus;
- Grafana.

---

# 40. DORA Metrics

## Métricas

- Deployment Frequency;
- Lead Time for Changes;
- Change Failure Rate;
- Mean Time to Recovery.

## Objetivo

Medir madurez DevOps de SBM Suite.

---

# 41. Roadmap de implementación

## Etapa 1 — Base

1. logs estructurados;
2. correlation IDs;
3. health endpoints;
4. métricas básicas;
5. Prometheus;
6. Grafana.

## Etapa 2 — Centralización

1. Loki;
2. Tempo;
3. OpenTelemetry Collector;
4. dashboards por servicio;
5. alertas básicas.

## Etapa 3 — Datos y mensajería

1. PostgreSQL exporter;
2. Redis exporter;
3. Celery metrics;
4. Kafka metrics;
5. Qdrant metrics.

## Etapa 4 — IA

1. Langfuse;
2. tokens;
3. costo;
4. prompts;
5. tools;
6. RAG evaluation;
7. agent traces.

## Etapa 5 — Operación avanzada

1. SLO;
2. error budgets;
3. synthetic monitoring;
4. runbooks;
5. postmortems;
6. DORA metrics.

---

# 42. Prioridad actual

## Urgente

1. logs estructurados;
2. correlation IDs;
3. health checks;
4. métricas de APIs;
5. dashboards iniciales;
6. monitoreo de errores.

## Corto plazo

1. Prometheus;
2. Grafana;
3. Loki;
4. Tempo;
5. Alertmanager;
6. PostgreSQL metrics.

## Mediano plazo

1. Redis;
2. Celery;
3. Kafka;
4. Kubernetes;
5. Langfuse;
6. SLO.

---

# 43. Evidencia para portafolio

## Entregables

- dashboard general;
- dashboard de APIs;
- dashboard PostgreSQL;
- dashboard Celery;
- dashboard Kafka;
- dashboard Kubernetes;
- dashboard IA;
- trazas distribuidas;
- alertas;
- runbooks;
- postmortem de ejemplo;
- reporte DORA.

---

# 44. Criterio de finalización

Una capacidad se considera observable cuando:

1. emite logs;
2. emite métricas;
3. genera trazas cuando corresponde;
4. mantiene correlation IDs;
5. tiene dashboard;
6. tiene alertas;
7. tiene runbook;
8. protege datos;
9. está documentada;
10. puede demostrarse.

---

# 45. Visión final

```
Logs
  +
Metrics
  +
Traces
  +
Business Signals
  +
AI Signals
  +
Automated Alerts
```

SBM Suite debe evolucionar hacia una plataforma donde cada servicio, integración, agente y proceso pueda observarse de extremo a extremo, permitiendo detectar fallas, entender impacto y responder rápidamente.

---

# 46. SBM-CONTROL operating model — 2026-08-16

`SBM-CONTROL` is the planned global operations control plane for application/service health, logs, reports/metrics, cron/schedulers, workers/queues, Kafka/Redis/Celery state, Context/Objectives/Documentation, QA, Security, deployments, alerts and DB/backups. It observes/orchestrates approved operations but does not own underlying business logic.
