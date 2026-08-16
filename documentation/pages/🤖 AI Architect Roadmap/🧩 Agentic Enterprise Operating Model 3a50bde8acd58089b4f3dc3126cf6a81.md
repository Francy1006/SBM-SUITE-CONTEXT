# 🧩 Agentic Enterprise Operating Model

> Modelo operativo empresarial basado en agentes para SBM Suite.
> 
> 
> Esta página define cómo humanos, agentes IA, APIs, herramientas, datos, flujos y controles trabajarán de forma coordinada dentro de una empresa multimarcas.
> 
> El objetivo no es reemplazar completamente a las personas, sino construir una organización más pequeña, automatizada, observable y escalable, donde los agentes ejecuten trabajo repetitivo y los humanos mantengan control sobre decisiones críticas.
> 

---

# 1. Objetivo

Diseñar un modelo operativo capaz de:

- coordinar múltiples agentes;
- automatizar procesos empresariales;
- asignar responsabilidades;
- mantener control humano;
- operar varias marcas;
- reducir trabajo manual;
- centralizar conocimiento;
- integrar herramientas;
- auditar acciones;
- escalar sin aumentar proporcionalmente la estructura humana;
- generar una visión empresarial asistida por IA.

---

# 2. Visión

```
Human Leadership
       +
AI Agent Workforce
       +
SBM Suite
       +
APIs and Tools
       +
Automation
       +
Observability
       +
Governance
```

SBM Suite debe convertirse en el sistema operativo central de una organización agentic y multimarcas.

---

# 3. Principios

1. **Human-controlled autonomy**
    
    La IA ejecuta, pero los humanos conservan control sobre decisiones críticas.
    
2. **Specialized agents**
    
    Cada agente debe tener un propósito limitado.
    
3. **Least privilege**
    
    Cada agente recibe solo las herramientas y permisos necesarios.
    
4. **API-first execution**
    
    Los agentes actúan mediante APIs y tools autorizadas.
    
5. **No direct database access**
    
    Los agentes no deben escribir directamente en bases de datos.
    
6. **Brand isolation**
    
    Todo acceso debe respetar límites por marca.
    
7. **Traceability**
    
    Cada decisión y acción debe quedar registrada.
    
8. **Progressive autonomy**
    
    La autonomía aumenta solo después de validar seguridad y confiabilidad.
    
9. **Human approval**
    
    Operaciones de alto riesgo requieren aprobación explícita.
    
10. **Observable behavior**
    
    Toda ejecución debe ser medible y auditable.
    

---

# 4. Modelo general

```
Board / Leadership
        │
        ▼
Executive Assistant Agent
        │
        ▼
Agent Orchestrator
        │
        ├── Finance Agent
        ├── Accounting Agent
        ├── Marketing Agent
        ├── Sales Agent
        ├── Operations Agent
        ├── Inventory Agent
        ├── Procurement Agent
        ├── Customer Service Agent
        ├── QA Agent
        ├── Security Agent
        ├── DevOps Agent
        └── Analytics Agent
        │
        ▼
SBM Suite APIs / MCP / Workflows / Data
```

---

# 5. Human operating model

## Human roles

- leadership;
- architecture;
- business ownership;
- finance approval;
- legal review;
- security oversight;
- exception handling;
- final decisions;
- strategic planning.

## Human responsibilities

- define goals;
- approve policies;
- supervise agents;
- review critical actions;
- resolve ambiguity;
- audit results;
- intervene in failures;
- adjust priorities.

---

# 6. AI workforce model

## Agents as digital workers

Cada agente debe tener:

- role;
- purpose;
- scope;
- tools;
- permissions;
- memory;
- risk level;
- approval rules;
- metrics;
- owner;
- fallback.

## Ejemplo

```
Agent: Inventory Agent
Purpose: monitor stock and suggest replenishment
Tools: inventory API, supplier API, analytics
Risk: medium
Approval: required before purchase order
Owner: Operations
```

---

# 7. Agent hierarchy

## Executive level

- Executive Assistant Agent;
- Analytics Agent;
- Strategy Agent futuro.

## Business level

- Finance Agent;
- Accounting Agent;
- Marketing Agent;
- Sales Agent;
- Operations Agent;
- Customer Service Agent;
- Inventory Agent;
- Procurement Agent.

## Technical level

- QA Agent;
- Security Agent;
- DevOps Agent;
- Documentation Agent;
- Azure Boards Agent.

## Integration level

- SBM API Integration Agent;
- Notion Documentation Agent;
- Jira Business Agent;
- Marketplace Agent;
- Tax Integration Agent.

---

# 8. Agent Orchestrator

## Objetivo

Coordinar agentes y decidir cuál debe responder o ejecutar.

## Responsabilidades

- detectar intención;
- seleccionar agente;
- validar permisos;
- validar marca;
- planificar flujo;
- ejecutar tools;
- solicitar aprobación;
- registrar resultado;
- manejar errores;
- aplicar fallback.

## Arquitectura

```
Request
  ↓
Intent Router
  ↓
Policy Layer
  ↓
Agent Orchestrator
  ↓
Selected Agent
  ↓
Tool Execution
  ↓
Validation
  ↓
Response
```

---

# 9. Intent Router

## Objetivo

Clasificar solicitudes.

## Categorías

- technical;
- commercial;
- financial;
- operational;
- documentation;
- support;
- security;
- analytics;
- marketing;
- tax;
- inventory;
- procurement.

## Requisitos

- confidence score;
- fallback;
- ambiguity handling;
- audit;
- brand context;
- user context.

---

# 10. Tool Router

## Objetivo

Seleccionar la herramienta adecuada.

## Tipos

- REST API;
- MCP;
- database read through API;
- workflow;
- external API;
- scheduler;
- event;
- document search;
- notification.

## Reglas

- allowlist;
- input schema;
- output schema;
- timeout;
- retries;
- permissions;
- audit.

---

# 11. Permission and Policy Layer

## Objetivo

Aplicar reglas antes de cada acción.

## Validaciones

- user identity;
- role;
- brand;
- resource;
- operation;
- risk;
- environment;
- approval;
- data sensitivity;
- time constraints.

## Resultado

```
allow
deny
require_approval
require_more_information
```

---

# 12. Risk model

| Risk Level | Example | Control |
| --- | --- | --- |
| Low | consulta de información | automático |
| Medium | creación de borrador | revisión opcional |
| High | modificación de datos | aprobación obligatoria |
| Critical | pagos, DTE, producción | doble aprobación y auditoría |

---

# 13. Human Approval

## Casos obligatorios

- pagos;
- transferencias;
- emisión tributaria;
- cambio de precios;
- publicación masiva;
- eliminación;
- permisos;
- despliegue productivo;
- cambios de infraestructura;
- contratación;
- acciones legales;
- compras importantes.

## Flujo

```
Agent Proposal
      ↓
Validation
      ↓
Approval Request
      ↓
Human Review
      ↓
Approved / Rejected
      ↓
Execution
      ↓
Audit
```

---

# 14. Executive Assistant Agent

## Objetivo

Servir como interfaz ejecutiva de la plataforma.

## Responsabilidades

- resumir estado de la empresa;
- consolidar KPIs;
- detectar alertas;
- preparar reuniones;
- ordenar prioridades;
- coordinar agentes;
- solicitar aprobaciones;
- generar reportes ejecutivos;
- seguir tareas críticas.

## Límites

- no toma decisiones financieras autónomas;
- no modifica políticas;
- no aprueba acciones críticas;
- no accede a datos sin permiso.

---

# 15. Documentation Agent

## Responsabilidades

- actualizar documentación;
- generar resúmenes;
- mantener decisiones;
- registrar arquitectura;
- mantener roadmap;
- sincronizar Notion, Confluence y Wiki;
- detectar documentación desactualizada.

## Herramientas

- Notion API;
- Confluence API;
- Azure DevOps Wiki;
- MCP;
- Git repositories.

---

# 16. Finance Agent

## Responsabilidades

- resumir flujo;
- detectar vencimientos;
- preparar proyecciones;
- identificar desviaciones;
- generar reportes;
- sugerir acciones;
- monitorear presupuesto.

## Límites

- no ejecutar pagos;
- no aprobar presupuestos;
- no modificar cuentas;
- no emitir documentos tributarios.

---

# 17. Accounting Agent

## Responsabilidades

- clasificar documentos;
- sugerir cuentas;
- preparar borradores de asientos;
- detectar inconsistencias;
- conciliar;
- generar checklists;
- resumir períodos.

## Límites

- no cerrar períodos;
- no contabilizar irreversiblemente;
- no presentar declaraciones;
- requiere revisión profesional.

---

# 18. Marketing Agent

## Responsabilidades

- proponer campañas;
- definir audiencias;
- generar briefs;
- analizar resultados;
- proponer contenido;
- detectar oportunidades;
- recomendar canales.

## Límites

- no aprobar presupuesto;
- no publicar sin política;
- no modificar precios;
- no utilizar datos no autorizados.

---

# 19. Content Agent

## Responsabilidades

- redactar copys;
- generar guiones;
- adaptar tono;
- generar metadata;
- producir prompts;
- resumir contenido;
- crear variantes.

## Límites

- no publicar automáticamente contenido sensible;
- no usar material sin licencia;
- requiere validación de marca.

---

# 20. Social Media Agent

## Responsabilidades

- preparar publicaciones;
- programar;
- adaptar formatos;
- recopilar métricas;
- responder casos simples;
- escalar casos sensibles.

## Límites

- no gestionar crisis de forma autónoma;
- no responder temas legales;
- no publicar datos sensibles;
- no eliminar comentarios críticos sin aprobación.

---

# 21. Sales Agent

## Responsabilidades

- clasificar leads;
- recomendar seguimiento;
- preparar propuestas;
- resumir oportunidades;
- detectar clientes inactivos;
- sugerir productos o servicios.

## Límites

- no cerrar contratos;
- no ofrecer descuentos no autorizados;
- no modificar precios;
- no acceder a datos fuera de su scope.

---

# 22. Customer Service Agent

## Responsabilidades

- responder FAQ;
- clasificar solicitudes;
- generar tickets;
- consultar estados;
- derivar;
- resumir conversaciones;
- detectar urgencias.

## Escalamiento obligatorio

- reclamos graves;
- temas legales;
- devoluciones complejas;
- seguridad;
- pagos;
- datos personales;
- crisis.

---

# 23. Inventory Agent

## Responsabilidades

- monitorear stock;
- detectar quiebres;
- sugerir reposición;
- detectar sobrestock;
- analizar rotación;
- alertar anomalías.

## Límites

- no comprar;
- no ajustar stock crítico;
- no modificar costos;
- no aprobar transferencias.

---

# 24. Procurement Agent

## Responsabilidades

- solicitar cotizaciones;
- comparar proveedores;
- preparar órdenes;
- identificar vencimientos;
- resumir condiciones;
- detectar oportunidades de ahorro.

## Límites

- no aprobar compras;
- no seleccionar proveedor sin política;
- no ejecutar pagos;
- no firmar contratos.

---

# 25. Operations Agent

## Responsabilidades

- revisar estado de proyectos;
- detectar bloqueos;
- generar checklists;
- crear tareas;
- controlar vencimientos;
- coordinar inspecciones;
- resumir incidencias.

## Límites

- no aprobar permisos;
- no cerrar inspecciones críticas;
- no modificar presupuestos;
- no cambiar planos sin revisión.

---

# 26. Franchise Agent

## Responsabilidades

- seguimiento de franquiciados;
- documentación;
- checklists;
- estándares;
- aperturas;
- soporte;
- alertas;
- cumplimiento operativo.

---

# 27. Legal and Compliance Agent

## Responsabilidades

- identificar documentos faltantes;
- controlar vencimientos;
- generar checklists;
- resumir obligaciones;
- preparar expedientes;
- alertar riesgos.

## Límites

- no reemplaza asesoría legal;
- no declara cumplimiento definitivo;
- no presenta documentación sin aprobación.

---

# 28. Tax Integration Agent

## Responsabilidades

- revisar estados DTE;
- detectar rechazos;
- preparar reintentos;
- resumir errores;
- alertar documentos pendientes;
- consultar proveedor.

## Límites

- no modificar datos tributarios sin autorización;
- no emitir documentos críticos automáticamente;
- no interpretar normativa como fuente definitiva.

---

# 29. Marketplace Agent

## Responsabilidades

- monitorear publicaciones;
- detectar diferencias de stock;
- preparar cambios de precio;
- revisar preguntas;
- resumir pedidos;
- detectar errores de sincronización;
- generar alertas.

## Límites

- no publicar precio sin reglas;
- no pausar masivamente sin aprobación;
- no responder casos sensibles;
- no modificar stock base.

---

# 30. Scheduling Agent

## Responsabilidades

- coordinar reuniones;
- agendar inspecciones;
- agendar operativos;
- recordar vencimientos;
- verificar disponibilidad;
- enviar notificaciones.

## Integraciones

- Google Calendar;
- Microsoft Calendar;
- APIs internas;
- n8n.

---

# 31. HR Agent

## Responsabilidades futuras

- onboarding;
- documentación;
- seguimiento de capacitaciones;
- recordatorios;
- solicitudes;
- FAQ internas;
- resúmenes.

## Límites

- no contratar;
- no despedir;
- no modificar remuneraciones;
- no tomar decisiones sensibles.

---

# 32. Analytics Agent

## Responsabilidades

- consolidar KPIs;
- interpretar dashboards;
- detectar tendencias;
- comparar marcas;
- generar reportes;
- identificar anomalías;
- explicar métricas.

## Regla

Debe citar fuentes y distinguir datos reales de inferencias.

---

# 33. QA Agent

## Responsabilidades

- generar casos de prueba;
- revisar cobertura;
- detectar regresiones;
- resumir resultados;
- crear bugs;
- priorizar fallos;
- validar criterios.

## Límites

- no aprobar releases por sí solo;
- no modificar producción;
- no ocultar fallos.

---

# 34. Security Agent

## Responsabilidades

- resumir hallazgos;
- analizar scans;
- crear vulnerabilidades;
- priorizar;
- detectar secretos;
- revisar configuraciones;
- generar alertas.

## Límites

- no explotar sistemas productivos;
- no modificar permisos sin aprobación;
- no ejecutar acciones destructivas.

---

# 35. DevOps Agent

## Responsabilidades

- consultar pipelines;
- resumir fallos;
- generar diagnósticos;
- preparar despliegues;
- recomendar rollback;
- revisar infraestructura;
- crear tareas técnicas.

## Límites

- no desplegar a producción sin aprobación;
- no modificar infraestructura crítica;
- no eliminar recursos;
- no rotar secretos autónomamente.

---

# 36. Memory model

## Tipos de memoria

- session memory;
- task memory;
- user preferences;
- agent state;
- business context;
- operational history.

## Reglas

- expiración;
- separación por usuario;
- separación por marca;
- minimización;
- auditabilidad;
- borrado;
- no reemplazar fuentes oficiales.

---

# 37. Knowledge model

## Fuentes

- Confluence;
- Notion;
- Azure DevOps Wiki;
- README;
- APIs;
- databases via services;
- dashboards;
- documents;
- events;
- policies.

## Regla

El conocimiento recuperado debe respetar permisos.

---

# 38. Multi-agent workflows

## Ejemplo: lanzamiento de producto

```
Product Agent
   ↓
Pricing Agent
   ↓
Inventory Agent
   ↓
Marketing Agent
   ↓
Content Agent
   ↓
Marketplace Agent
   ↓
Human Approval
   ↓
Publication
```

## Ejemplo: apertura de sucursal

```
Operations Agent
   ↓
Compliance Agent
   ↓
Procurement Agent
   ↓
Finance Agent
   ↓
Documentation Agent
   ↓
Human Approval
```

---

# 39. Agent communication

## Opciones

- direct orchestration;
- event-driven;
- shared task state;
- workflows;
- message queue;
- Kafka;
- Celery;
- MCP.

## Principio

Evitar conversaciones libres entre agentes sin control.

---

# 40. Event-driven agent model

## Eventos

```
order.created
stock.low
invoice.rejected
campaign.completed
task.blocked
security.finding.created
pipeline.failed
permit.expiring
```

## Flujo

```
Event
  ↓
Policy Check
  ↓
Agent Trigger
  ↓
Action or Recommendation
  ↓
Approval
  ↓
Audit
```

---

# 41. Agent state machine

## Estados

```
idle
planning
waiting_for_tool
waiting_for_approval
executing
completed
failed
cancelled
```

## Requisitos

- timeout;
- retries;
- resume;
- cancellation;
- audit;
- idempotencia.

---

# 42. Failure handling

## Casos

- tool unavailable;
- API timeout;
- permission denied;
- invalid output;
- low confidence;
- conflicting data;
- external error;
- partial execution.

## Acciones

- retry;
- fallback;
- human escalation;
- cancellation;
- partial rollback;
- incident creation.

---

# 43. Governance

## Cada agente debe tener

- owner;
- purpose;
- version;
- permissions;
- tools;
- datasets;
- prompts;
- metrics;
- risks;
- approval policy;
- rollback;
- deactivation procedure.

---

# 44. Agent registry

## Objetivo

Mantener catálogo central.

## Campos

- agent ID;
- name;
- domain;
- owner;
- status;
- version;
- risk;
- tools;
- scopes;
- model;
- prompt version;
- environment;
- last review.

---

# 45. Agent lifecycle

```
Proposed
  ↓
Designed
  ↓
Tested
  ↓
Approved
  ↓
Deployed
  ↓
Monitored
  ↓
Reviewed
  ↓
Updated or Retired
```

---

# 46. Agent testing

## Niveles

- unit;
- tool;
- integration;
- scenario;
- regression;
- security;
- red teaming;
- human evaluation.

## Casos

- éxito;
- error;
- ambigüedad;
- acceso no autorizado;
- prompt injection;
- tool incorrecta;
- timeout;
- operación parcial;
- baja confianza.

---

# 47. Agent observability

## Métricas

- executions;
- success rate;
- failure rate;
- latency;
- tokens;
- cost;
- tool calls;
- retries;
- approval time;
- escalations;
- confidence;
- user feedback.

---

# 48. Agent security

## Controles

- tool allowlist;
- input validation;
- output validation;
- permissions;
- brand scope;
- rate limits;
- timeout;
- human approval;
- sandbox;
- audit;
- memory controls.

---

# 49. OpenClaw in the operating model

## Rol

OpenClaw puede actuar como gateway multicanal opcional.

## Flujo

```
Slack / WhatsApp / Teams / Telegram
                ↓
             OpenClaw
                ↓
        SBM-AI-ASSISTANT
                ↓
        Agent Orchestrator
```

## Regla

OpenClaw no coordina la lógica empresarial central ni reemplaza el orquestador.

---

# 50. Digital workplace

## Interfaces

- Slack;
- Teams;
- WhatsApp;
- web portal;
- dashboards;
- mobile app;
- email;
- voice future.

## Objetivo

Permitir que usuarios interactúen con SBM Suite en lenguaje natural.

---

# 51. Work management

## Plataformas

- Azure Boards para desarrollo;
- Jira para negocio;
- Notion para roadmap;
- Azure DevOps Wiki para documentación técnica;
- SBM Suite para operación;
- Calendar para agenda.

## Agentes

Cada plataforma debe tener un agente o integración con límites claros.

---

# 52. Decision support

## Tipos de decisión

- operational;
- financial;
- commercial;
- technical;
- strategic.

## Modelo

```
Data
  ↓
Analysis
  ↓
Agent Recommendation
  ↓
Human Decision
  ↓
Execution
  ↓
Outcome
```

---

# 53. Autonomous actions

## Permitidas inicialmente

- consultas;
- resúmenes;
- creación de borradores;
- creación de tareas;
- recordatorios;
- clasificación;
- alertas.

## Permitidas posteriormente

- actualizaciones de bajo riesgo;
- sincronizaciones;
- respuestas simples;
- programación;
- reintentos.

## Siempre restringidas

- pagos;
- cambios legales;
- eliminación masiva;
- despliegues críticos;
- emisión tributaria sensible;
- cambios de seguridad.

---

# 54. Enterprise metrics

## Métricas

- porcentaje de tareas automatizadas;
- tiempo ahorrado;
- errores evitados;
- costo por proceso;
- agent success rate;
- human escalation rate;
- approval time;
- throughput;
- ROI;
- satisfacción del usuario.

---

# 55. Organizational impact

## Beneficios esperados

- menor carga administrativa;
- mayor velocidad;
- mejor trazabilidad;
- operación multimarcas;
- menos duplicación;
- decisiones informadas;
- capacidad de escalar;
- estructura humana más eficiente.

## Riesgos

- dependencia excesiva;
- automatización incorrecta;
- permisos amplios;
- falta de supervisión;
- datos incorrectos;
- costos LLM;
- complejidad operativa.

---

# 56. Roadmap de implementación

## Etapa 1 — Foundation

1. Intent Router;
2. Tool Router;
3. Permission Layer;
4. audit;
5. human approval;
6. agent registry.

## Etapa 2 — Initial agents

1. SBM API Integration Agent;
2. Azure Boards Agent;
3. Notion Documentation Agent;
4. Jira Business Agent;
5. Documentation Agent.

## Etapa 3 — Business agents

1. Finance Agent;
2. Marketing Agent;
3. Sales Agent;
4. Operations Agent;
5. Customer Service Agent;
6. Inventory Agent.

## Etapa 4 — Technical agents

1. QA Agent;
2. Security Agent;
3. DevOps Agent;
4. Analytics Agent;
5. Compliance Agent.

## Etapa 5 — Advanced orchestration

1. multi-agent workflows;
2. event-driven agents;
3. memory;
4. cross-domain coordination;
5. progressive autonomy;
6. executive assistant.

---

# 57. Prioridad actual

## Urgente

1. integrar APIs;
2. definir tools;
3. implementar permisos;
4. implementar audit;
5. human approval;
6. Azure Boards Agent;
7. Notion Agent;
8. Jira Agent.

## Corto plazo

1. LangGraph;
2. agent registry;
3. observability;
4. documentation;
5. Finance Agent;
6. Operations Agent.

## Mediano plazo

1. agentes especializados;
2. workflows multiagente;
3. event-driven agents;
4. OpenClaw;
5. analytics;
6. executive assistant.

## Largo plazo

1. mayor autonomía;
2. voz;
3. coordinación empresarial;
4. optimización automática;
5. empresa supervisada por agentes.

---

# 58. Evidencia para portafolio

## Entregables

- agent architecture;
- agent registry;
- permission model;
- approval workflow;
- audit logs;
- multi-agent demo;
- technical agent;
- business agent;
- dashboards;
- security tests;
- video de operación.

---

# 59. Criterio de finalización

Un agente se considera productivo cuando:

1. tiene objetivo claro;
2. tiene owner;
3. tiene tools limitadas;
4. tiene permisos;
5. tiene pruebas;
6. tiene seguridad;
7. tiene observabilidad;
8. tiene auditoría;
9. tiene fallback;
10. tiene aprobación cuando corresponde;
11. está documentado;
12. puede desactivarse;
13. puede demostrarse.

---

# 60. Visión final

```
Human Leadership
        +
Specialized AI Agents
        +
SBM Suite
        +
Automation
        +
Governance
        +
Observability
```

SBM Suite debe evolucionar hacia un sistema operativo empresarial multimarcas donde una fuerza de trabajo digital especializada ejecute procesos, genere recomendaciones y coordine operaciones bajo supervisión humana, permisos mínimos y trazabilidad completa.

---

# 61. Canonical named-agent operating model — 2026-08-16

This section supersedes generic role names in earlier roadmap sections when there is a conflict. The canonical catalog contains 53 named agents. Agents are definitions/capabilities, not permanently running processes.

## Execution principle

```text
API/service/job/cron deterministic solution first
→ agent only when reasoning/ambiguity/high-value analysis is required
→ Scrum Agent + orchestration decides activation
→ least privilege + audit + explicit governance
```

`SBM Agent` consolidates suite-level processes. `Scrum Agent` coordinates async processes, priorities and dependencies. `Tesla Agent` implements; `Edison Agent` independently challenges technical choices; `Igor Agent` owns technical QA/DevOps/SRE; `Armstrong Agent` coordinates deploy/release. Security is led by `Batman Agent` with specialized Blue/Red/Threat/Email roles. `Snape Agent` is governed directly by `sbm-admin` and audits CEO/governance independently of Batman.

Brand agents (`DP Agent`, `KS Agent`, `PC Agent`, `CG Agent`) protect only their own brand and communicate through SBM Manager / `sbm-admin`; specialist internal-agent processes are consolidated through SBM Manager.

## Canonical catalog

| N° | Agente | Gobierno | Responsabilidad | Apps / fuentes principales |
|---:|---|---|---|---|
| 1 | CEO Agent | Primordial | Dirección estratégica, decisiones y autorizaciones finales. | sbm-admin ; SBM-MANAGER ; reportes |
| 2 | SBM Agent | Primordial | Orquesta y consolida procesos, dominios, agentes y marcas. | SBM-CORE ; Control API ; SBM-MANAGER ; sbm-admin |
| 3 | CFO Agent | CEO | Evalúa finanzas, tecnología, riesgos y autorizaciones económicas. | sbm-admin ; Finanzas ; Procurement ; reportes |
| 4 | Snape Agent | sbm-admin | Audita independientemente al CEO y escala desviaciones. | sbm-admin ; audit logs ; reportes ; Context/Documentation |
| 5 | Jarvis Agent | CEO | Asiste al CEO con síntesis, métricas, decisiones y seguimiento. | sbm-admin ; Galileo/read-model ; reportes |
| 6 | Spock Agent | CFO | Analiza trade-offs, riesgos y costo/beneficio para CFO. | Finanzas ; Sherlock ; Nostradamus ; sbm-admin |
| 7 | Scrum Agent | SBM | Coordina procesos asíncronos, prioridades, dependencias y activaciones IA. | SBM-CORE ; Control API ; Jira ; SBM-MANAGER |
| 8 | Sherlock Agent | SBM | Investiga tecnologías, amenazas, normativa, tendencias y evidencia nueva. | Web/search ; Knowledge Base ; Context ; Documentation |
| 9 | Nostradamus Agent | SBM | Realiza forecasting y predicciones estadísticas transversales. | Galileo/read-model ; históricos ; SBM-CORE |
| 10 | Darwin Agent | SBM | Entrena, evalúa, fine-tunea y mejora continuamente los agentes. | SBM-AI-ASSISTANT ; eval pipelines ; Sherlock ; Nostradamus |
| 11 | Tesla Agent | CFO + CEO | Diseña e implementa desarrollos autorizados. | Git repos ; CI ; project APIs ; SBM-CORE |
| 12 | Edison Agent | CFO | Desafía independientemente las decisiones tecnológicas de Tesla. | Git repos ; CI ; Sherlock ; Nostradamus |
| 13 | Igor Agent | Tesla | QA técnico, DevOps/SRE, infraestructura y troubleshooting. | CI/CD ; tests ; cloud ; observabilidad |
| 14 | Armstrong Agent | Tesla + Robin | Coordina deploy, release, readiness y rollback. | CI/CD ; cloud deploy ; repos ; releases |
| 15 | Batman Agent | CEO + sbm-admin | Patrulla, anticipa ataques, encuentra fallos y exige mejoras. | SBM-SECURITY-API ; SBM-SECURITY ; logs ; SBM-CORE |
| 16 | Alfred Agent | Batman | Gestiona requerimientos de seguridad y garantiza QA/CIA. | SBM-MANAGER ; QA ; repos ; SBM-SECURITY |
| 17 | Robin Agent | Batman | Protege integridad funcional/data, backups y coherencia documental. | Context ; Documentation ; backups ; object storage |
| 18 | Gotham Agent | Robin + Batman | Detecta diferencias entre SBM-SUITE real, Context y Documentation. | Context ; Documentation ; repos ; service inventory |
| 19 | Joker Agent | Batman / Control API | Ejecuta Red Team y pentesting autorizado contra SBM-SUITE. | Security lab ; pentest tools ; SBM-SECURITY-API ; logs |
| 20 | Queen Agent | Joker / Control API | Administra ambientes, herramientas y QA técnico de Joker. | Security lab ; CI/CD ; tools/APIs |
| 21 | Darth Maul Agent | Batman | Threat hunting y atribución de atacantes reales. | SBM-SECURITY-API ; logs ; threat intel ; Joker outputs |
| 22 | Cerberus Agent | Batman | Trata correo y adjuntos como hostiles y controla cuarentena. | SBM-UTIL mail ; sandbox ; SBM-SECURITY-API |
| 23 | Hercules Agent | Cerberus + MacGyver | Normaliza contenido sanitizado a formatos seguros para agentes. | SBM-UTIL ; parsers ; object storage |
| 24 | Murphy Agent | CFO + CEO | Gestiona riesgo transversal y escenarios adversos. | Risk register ; Operations ; Finance ; Security reports |
| 25 | Abagnale Agent | CFO + Batman | Detecta fraude, falsificación, suplantación y patrones anómalos. | Payments ; identity logs ; finance data ; Galileo |
| 26 | L Agent | Snape + sbm-admin | Auditoría investigativa, evidencias y reconstrucción de hechos. | audit logs ; Context ; Documentation ; reports |
| 27 | Belfort Agent | CEO | Lidera estrategia de Marketing/Sales, campañas, tendencias y métricas. | SBM-MARKETING ; Google Analytics ; Search Console ; social APIs |
| 28 | Stratton Agent | Belfort | Mano técnica de Marketing: ambientes, integraciones, QA y desarrollos. | SBM-MARKETING ; CI/CD ; social APIs ; integrations |
| 29 | Donnie Agent | Belfort | Ejecuta canales, redes, chatbot y atención externa. | SBM-MARKETING ; social APIs ; chatbot ; messaging |
| 30 | DaVinci Agent | Belfort | Produce contenido creativo, visual, frontend y campañas. | Blender ; Photoshop ; frontend repos ; asset storage |
| 31 | Medici Agent | Belfort | QA creativo, estándares, patrones, consistencia y tendencias. | asset storage ; design systems ; Sherlock |
| 32 | WallStreet Agent | CEO | Gestiona ventas, revenue, pipeline, conversión y forecast. | CRM/Sales ; sbm-admin ; Galileo |
| 33 | Rockefeller Agent | CFO | Controla gastos, costos, consumo y cotizaciones. | Finance ; cloud billing ; Procurement ; sbm-admin |
| 34 | Buffett Agent | CFO | Presupuestos, proyecciones, austeridad y optimización de costos. | Finance ; pricing/cost sources ; sbm-admin |
| 35 | Burns Agent | CFO | Normativa contable/fiscal, monedas, UF/USD y estructuras. | SII ; Accounting ; FX/UF ; sbm-admin |
| 36 | Smithers Agent | Burns | Operación contable, facturas, respaldos y faltantes. | Accounting ; SII ; Records |
| 37 | Frink Agent | Burns | Tecnología, integraciones, ambientes y deploys contables. | Accounting integrations ; SBM-UTIL ; CI/CD ; Tesla |
| 38 | Midas Agent | CFO | Tesorería: caja, pagos, cobranza, conciliación y liquidez. | Finance ; bank/payment APIs ; Accounting |
| 39 | Galileo Agent | SBM + CEO | KPIs, analytics, calidad de datos y read-model multimarcas. | Data warehouse ; Analytics ; brand data |
| 40 | MacGyver Agent | SBM + Tesla | Integraciones, conectores, email, archivos y APIs determinísticas. | SBM-UTIL ; external APIs ; mail/files |
| 41 | Blackbeard Agent | CFO + Mario | Procurement, proveedores, OC, logística, aduana y supply chain. | Procurement ; supplier APIs/docs ; Logistics |
| 42 | Gringotts Agent | Mario | Gestiona inventario, stock, bodegas, equipos y activos. | Inventory/Assets ; warehouse data ; SBM-MANAGER |
| 43 | Hermione Agent | Robin | Records, documentos, assets, versionado, retención y archivo. | Object Storage ; Records ; Documentation |
| 44 | Sparrow Agent | Blackbeard + CEO | Investiga mercados, proveedores, rutas, riesgos y costos de importación. | Procurement/import ; research ; freight/customs |
| 45 | Barbossa Agent | Blackbeard + CEO | Gestiona importaciones, embarques, aduana, documentos y atrasos. | Import/Logistics ; customs/freight ; Procurement |
| 46 | Mario Agent | SBM | Gestiona operaciones, atrasos, procesos, cotizaciones, KPIs y estimaciones. | Operations ; SBM-MANAGER ; operational read-model |
| 47 | Luigi Agent | Mario | Genera diagramas, formatos, reportes y documentación operacional. | Operations ; diagram/report tools ; Documentation |
| 48 | Harvey Agent | CEO | Legal: contratos, riesgos jurídicos y análisis legal. | Legal docs ; contracts ; sbm-admin ; Hermione |
| 49 | Louis Agent | CEO | Compliance, controles, obligaciones y evidencia regulatoria. | Compliance ; audit logs ; regulatory sources ; sbm-admin |
| 50 | DP Agent | Admin DP + SBM Manager | Vela exclusivamente por los intereses de DP. | SBM-MANAGER ; sbm-admin |
| 51 | KS Agent | Admin KS + SBM Manager | Vela exclusivamente por los intereses de KS. | SBM-MANAGER ; sbm-admin |
| 52 | PC Agent | Admin PC + SBM Manager | Vela exclusivamente por los intereses de PC. | SBM-MANAGER ; sbm-admin |
| 53 | CG Agent | Admin CG + SBM Manager | Vela exclusivamente por los intereses de CG. | SBM-MANAGER ; sbm-admin |

## Related implementation objective

`OBJ-CTX-034` expands `SBM-AI-ASSISTANT` to register/govern this catalog, its hierarchy, permissions, tools and on-demand activation without making agents the default automation mechanism.
