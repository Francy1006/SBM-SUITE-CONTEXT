# 🤖AI-Engineering

> Roadmap de ingeniería de Inteligencia Artificial para SBM Suite.
> 
> 
> Esta página define la arquitectura, capacidades, herramientas, agentes, controles y evolución de `SBM-AI-ASSISTANT` como orquestador central de IA, RAG, tools, APIs, MCP y agentes especializados.
> 
> El objetivo no es agregar IA como una función aislada, sino integrarla de forma segura, observable y útil dentro de los procesos reales de la plataforma.
> 

---

# 1. Objetivo

Convertir `SBM-AI-ASSISTANT` en una capa inteligente transversal capaz de:

- responder preguntas empresariales;
- consultar documentación;
- consultar APIs internas y cliente;
- ejecutar herramientas autorizadas;
- crear y actualizar tareas;
- mantener documentación;
- coordinar agentes especializados;
- asistir procesos operativos;
- automatizar flujos;
- generar recomendaciones;
- solicitar aprobación humana cuando corresponda.

---

# 2. Estado actual

Actualmente `SBM-AI-ASSISTANT` incluye:

- FastAPI;
- RAG documental;
- integración con Confluence;
- embeddings multilingües;
- Qdrant;
- Slack como interfaz;
- Cohere como LLM;
- sincronización programada;
- respuestas basadas en documentación empresarial;
- arquitectura inicial separada por rutas;
- soporte para ingestión y sincronización de contenido.

## Limitaciones actuales

- no consulta todavía `SBM-API`;
- no consulta todavía `DP-API`;
- no dispone de un router completo de intención;
- no dispone de tools empresariales consolidadas;
- no dispone de agentes especializados;
- no dispone de integración con Azure Boards;
- no dispone de integración con Notion;
- no dispone de integración operativa con Jira;
- no dispone de observabilidad LLM completa;
- no dispone de evaluación automática;
- no dispone de una capa formal de políticas y permisos;
- el scheduler actual debe migrarse cuando se incorpore Celery Beat.

---

# 3. Arquitectura objetivo

```
Usuario
   │
   ▼
Slack / Chat / Web / Canales externos
   │
   ▼
Multichannel Gateway opcional
   │
   ▼
SBM-AI-ASSISTANT
   │
   ├── Intent Router
   ├── Tool Router
   ├── Agent Orchestrator
   ├── RAG Engine
   ├── API Clients
   ├── MCP Clients
   ├── Permission and Policy Layer
   ├── Human Approval
   ├── Audit and Observability
   └── LLM Provider Layer
```

## Capas principales

| Capa | Responsabilidad |
| --- | --- |
| Channel Layer | Recibir solicitudes desde Slack, web, WhatsApp, Teams u otros canales |
| Intent Router | Detectar intención y clasificar la solicitud |
| Tool Router | Seleccionar la herramienta o integración adecuada |
| Agent Orchestrator | Coordinar agentes y flujos complejos |
| RAG Engine | Recuperar conocimiento empresarial |
| API Clients | Consumir `SBM-API`, `DP-API` y futuras APIs cliente |
| MCP Clients | Consumir servidores MCP autorizados |
| Policy Layer | Validar permisos, marca, alcance y riesgo |
| Human Approval | Confirmar operaciones críticas |
| Observability | Registrar trazas, costos, errores y resultados |
| LLM Provider Layer | Permitir múltiples proveedores y modelos locales |

---

# 4. Orden de implementación

## 1. SBM API Integration Agent

Primera integración operativa prioritaria.

### Responsabilidades

- detectar intención;
- decidir entre `SBM-API` y `DP-API`;
- consumir endpoints mediante tools controladas;
- validar autenticación;
- validar permisos;
- validar marca y alcance;
- transformar respuestas técnicas en lenguaje natural;
- registrar solicitudes y errores;
- comenzar con consultas de solo lectura;
- solicitar confirmación para operaciones de escritura;
- preparar soporte para futuras APIs cliente.

### Flujo

```
Usuario
   ↓
SBM-AI-ASSISTANT
   ↓
Intent Router
   ↓
SBM API Integration Agent
   ├── SBM-API
   └── DP-API
```

### Casos iniciales

- consultar productos;
- consultar materiales;
- consultar precios;
- consultar inventario;
- consultar sucursales;
- consultar clientes autorizados;
- consultar estados operativos;
- obtener resúmenes empresariales.

---

## 2. Azure Boards Agent

Responsable del backlog técnico.

### Responsabilidades

- consultar backlog;
- crear Product Backlog Items;
- crear bugs;
- crear tareas;
- generar criterios de aceptación;
- asignar prioridad;
- actualizar estados;
- vincular repositorios;
- vincular commits y pull requests;
- generar resúmenes de avance;
- consultar trabajo pendiente por proyecto.

### Principio

Azure Boards será la fuente oficial del backlog técnico.

---

## 3. Notion Documentation Agent

Responsable de la documentación general y el roadmap.

### Responsabilidades

- leer páginas autorizadas;
- crear secciones;
- reorganizar contenido;
- actualizar estados;
- registrar decisiones;
- mantener el roadmap;
- generar resúmenes;
- solicitar aprobación antes de cambios importantes;
- mantener trazabilidad.

### Integraciones

- Notion API;
- Notion MCP;
- permisos limitados;
- auditoría.

### Principio

Notion mantendrá la visión general, prioridades, aprendizaje y roadmap. La documentación técnica detallada migrará progresivamente hacia Azure DevOps Wiki y los repositorios.

---

## 4. Jira Business Agent

Responsable de tareas operativas y de negocio.

### Responsabilidades

- crear tareas operativas;
- registrar solicitudes internas;
- registrar campañas;
- registrar requerimientos comerciales;
- registrar requerimientos de clientes;
- actualizar estados;
- generar resúmenes operativos.

### Principio

Jira no será el backlog técnico principal.

---

## 5. OpenClaw Multichannel Gateway

Integración opcional para exponer `SBM-AI-ASSISTANT` en múltiples canales.

### Canales potenciales

- Slack;
- WhatsApp;
- Telegram;
- Microsoft Teams;
- otros canales compatibles.

### Responsabilidades

- recibir mensajes;
- mantener contexto de sesión;
- enrutar solicitudes;
- unificar canales;
- aplicar permisos mínimos;
- evitar acceso directo a APIs internas o bases de datos.

### Estado

- Research;
- Optional;
- posterior a integraciones prioritarias.

### Principio

OpenClaw no reemplaza:

- `SBM-AI-ASSISTANT`;
- LangGraph;
- MCP;
- el Intent Router;
- el Tool Router;
- la capa de permisos;
- la aprobación humana.

---

# 5. RAG

## Objetivo

Permitir que los usuarios consulten documentación empresarial actualizada y contextual.

## Fuentes actuales o planificadas

- Confluence;
- Notion;
- Azure DevOps Wiki;
- README;
- documentación técnica;
- manuales;
- procedimientos;
- políticas;
- documentos por marca.

## Componentes

| Componente | Función |
| --- | --- |
| Ingestion | Extraer contenido desde fuentes autorizadas |
| Cleaning | Limpiar contenido irrelevante |
| Chunking | Dividir documentos |
| Embeddings | Representar contenido semánticamente |
| Vector Store | Guardar y consultar vectores |
| Retrieval | Recuperar contexto |
| Filtering | Aplicar filtros por marca, usuario y estado |
| Generation | Generar respuesta con el LLM |
| Evaluation | Medir calidad |
| Observability | Registrar trazas |

## Estado actual

- Qdrant implementado;
- embeddings implementados;
- sincronización Confluence implementada;
- Slack implementado;
- filtros por estado implementados;
- versionado documental implementado parcialmente.

## Mejoras planificadas

- semantic chunking;
- hybrid search;
- re-ranking;
- query rewriting;
- contextual retrieval;
- filtros de seguridad;
- evaluación automática;
- datasets de prueba;
- protección contra prompt injection;
- trazabilidad documental.

---

# 6. LLM Providers

## Estrategia

Evitar dependencia de un solo proveedor.

## Proveedores contemplados

| Provider | Uso |
| --- | --- |
| Cohere | Proveedor actual |
| Ollama | Modelos locales |
| OpenAI | Producción o pruebas avanzadas |
| Anthropic | Producción o agentes |
| Azure OpenAI | Integración enterprise |
| Azure AI Foundry | Evaluación, agentes y despliegue |
| Gemini | Alternativa multimodal |
| AWS Bedrock | Plataforma enterprise futura |

## LLM Gateway

Se evaluará una capa como LiteLLM para:

- cambiar de proveedor;
- aplicar fallback;
- medir uso;
- controlar costos;
- normalizar llamadas;
- gestionar modelos locales y remotos.

---

# 7. Model Context Protocol

## Objetivo

Permitir que `SBM-AI-ASSISTANT` se conecte de forma estandarizada con herramientas y fuentes externas.

## Componentes

- MCP Client;
- MCP Server;
- MCP Tools;
- MCP Resources;
- MCP Prompts;
- autenticación;
- control de permisos;
- auditoría.

## Casos potenciales

- Notion MCP;
- Obsidian MCP;
- documentación interna;
- bases de conocimiento;
- servicios empresariales;
- herramientas de productividad;
- agentes de desarrollo.

## Principio

MCP no debe reemplazar indiscriminadamente APIs existentes. Se utilizará cuando agregue valor, estandarización o facilidad de integración.

---

# 8. Agent Architecture

## Agentes prioritarios

1. SBM API Integration Agent.
2. Azure Boards Agent.
3. Notion Documentation Agent.
4. Jira Business Agent.
5. OpenClaw Multichannel Gateway como integración opcional.

## Agentes especializados futuros

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

---

# 9. Modelo de ejecución de agentes

Cada agente debe definir:

| Elemento | Requisito |
| --- | --- |
| Purpose | Objetivo específico |
| Inputs | Datos aceptados |
| Outputs | Resultado esperado |
| Tools | Herramientas autorizadas |
| Permissions | Alcance mínimo |
| Brand Scope | Marcas autorizadas |
| Risk Level | Nivel de riesgo |
| Approval | Reglas de confirmación |
| Audit | Registro de ejecución |
| Errors | Manejo de fallas |
| Retries | Política de reintentos |
| Timeout | Tiempo máximo |
| Observability | Métricas y trazas |

## Reglas obligatorias

- sin acceso directo a la base de datos;
- sin permisos globales innecesarios;
- sin operaciones críticas sin confirmación;
- sin acceso cruzado entre marcas no autorizado;
- con trazabilidad;
- con validación de entradas;
- con validación de salida;
- con límites de ejecución;
- con políticas de fallback.

---

# 10. Tool Calling

## Objetivo

Exponer capacidades reales del sistema de forma controlada.

## Tipos de tools

- API tools;
- documentation tools;
- backlog tools;
- business task tools;
- analytics tools;
- notification tools;
- marketplace tools;
- finance tools;
- operations tools;
- security tools;
- QA tools.

## Estructura recomendada

```
Tool
├── Name
├── Description
├── Input Schema
├── Output Schema
├── Permissions
├── Brand Scope
├── Risk Level
├── Validation
├── Audit
└── Error Handling
```

---

# 11. Human-in-the-loop

## Objetivo

Evitar acciones irreversibles o críticas sin supervisión.

## Operaciones que requieren aprobación

- crear o modificar información sensible;
- emitir documentos tributarios;
- modificar precios;
- publicar campañas;
- publicar contenido;
- realizar acciones financieras;
- cambiar permisos;
- eliminar registros;
- desplegar a producción;
- modificar infraestructura;
- ejecutar acciones masivas;
- publicar en marketplaces;
- actualizar documentos críticos.

## Niveles de riesgo

| Nivel | Ejemplo | Control |
| --- | --- | --- |
| Bajo | Consultar información | Automático |
| Medio | Crear borrador o tarea | Confirmación opcional |
| Alto | Modificar datos | Confirmación obligatoria |
| Crítico | Finanzas, tributación, despliegues | Aprobación explícita y auditoría |

---

# 12. AI Security

## Riesgos principales

- prompt injection;
- data leakage;
- tool abuse;
- privilege escalation;
- cross-brand data access;
- malicious documents;
- unsafe outputs;
- insecure agent memory;
- unauthorized actions;
- secret exposure.

## Controles

- filtros de entrada;
- validación de contexto;
- control por marca;
- allowlist de tools;
- validación de schemas;
- output validation;
- human approval;
- rate limiting;
- sandboxing;
- logging;
- red teaming;
- evaluación automática.

## Herramientas

- OWASP Top 10 for LLM Applications;
- Garak;
- Promptfoo OSS;
- DeepEval;
- Ragas;
- Guardrails AI;
- Gitleaks;
- Trivy;
- Semgrep.

---

# 13. AI Observability

## Objetivo

Observar cada solicitud desde el canal hasta la respuesta final.

## Métricas

- latencia;
- tokens de entrada;
- tokens de salida;
- costo;
- modelo usado;
- tool seleccionada;
- errores;
- retries;
- calidad;
- contexto recuperado;
- aprobación humana;
- tasa de fallback;
- éxito de ejecución.

## Herramientas

- Langfuse Self-Hosted;
- OpenTelemetry;
- Prometheus;
- Grafana;
- Loki;
- Tempo;
- MLflow;
- structured logging;
- correlation IDs.

---

# 14. AI Evaluation

## Dimensiones

- exactitud;
- relevancia;
- groundedness;
- completitud;
- seguridad;
- consistencia;
- calidad del retrieval;
- calidad de tools;
- tiempo de respuesta;
- costo.

## Herramientas

- Ragas;
- DeepEval;
- Promptfoo;
- Langfuse;
- MLflow;
- datasets de evaluación;
- pruebas automatizadas;
- evaluaciones humanas.

## Tipos de evaluación

1. offline;
2. pre-deployment;
3. integration testing;
4. regression testing;
5. online monitoring;
6. human review.

---

# 15. Prompt Engineering

## Elementos a gestionar

- system prompts;
- role prompts;
- task prompts;
- tool descriptions;
- response schemas;
- safety rules;
- brand context;
- examples;
- fallback prompts.

## Requisitos

- versionado;
- pruebas;
- revisión;
- trazabilidad;
- rollback;
- evaluación;
- separación por entorno.

---

# 16. Memory

## Tipos

- short-term conversation memory;
- session context;
- user preferences;
- task memory;
- agent state;
- business context.

## Principios

- no almacenar información sensible sin necesidad;
- definir expiración;
- separar memoria por usuario y marca;
- permitir borrado;
- evitar que memoria reemplace fuentes oficiales;
- auditar su uso.

---

# 17. Scheduler y procesamiento asíncrono

## Estado actual

La sincronización de documentación utiliza un scheduler dentro de la aplicación.

## Evolución

Cuando se implemente Redis y Celery:

- Celery Worker ejecutará tareas;
- Celery Beat programará sincronizaciones;
- Flower permitirá monitoreo;
- Redis manejará broker y locks;
- se evitarán ejecuciones duplicadas con múltiples réplicas.

## Casos

- sincronización Confluence;
- actualización Notion;
- evaluación automática;
- generación de embeddings;
- generación documental;
- notificaciones;
- tareas de agentes;
- mantenimiento de índices.

---

# 18. Azure AI Foundry

## Prioridad

Alta, en paralelo al desarrollo.

## Formación urgente

**AI-3016: Develop generative AI apps in Azure AI Foundry portal**

## Objetivos

- comprender Model Catalog;
- desplegar modelos;
- trabajar con prompts;
- utilizar evaluaciones;
- explorar agentes;
- aplicar seguridad;
- conectar servicios;
- integrar conocimientos posteriormente en `SBM-AI-ASSISTANT`.

## Uso futuro en SBM Suite

- proveedor alternativo de modelos;
- evaluación de prompts;
- pruebas de agentes;
- seguridad;
- comparación con modelos locales;
- demostración enterprise.

---

# 19. Multimodal AI

## Capacidades futuras

- análisis de imágenes;
- OCR;
- lectura de documentos;
- clasificación visual;
- generación de imágenes;
- generación de contenido;
- análisis de planos;
- extracción de información;
- visión para operaciones;
- contenido de marketing.

## Herramientas

- OpenCV;
- OCR;
- YOLO;
- Hugging Face;
- ComfyUI;
- Azure AI;
- Gemini;
- modelos multimodales;
- Cloudinary.

---

# 20. AI for Business Domains

## Commerce

- recomendaciones;
- búsqueda semántica;
- asistentes de compra;
- sincronización de catálogos;
- análisis de precios.

## Operations

- análisis documental;
- clasificación de permisos;
- asistencia con planos;
- extracción de datos.

## Marketing

- briefs;
- copys;
- contenidos;
- segmentación;
- análisis de campañas.

## Finance

- forecasting;
- alertas;
- análisis de flujo;
- conciliación asistida.

## Accounting

- clasificación documental;
- revisión;
- integración tributaria;
- validación asistida.

## Customer Service

- FAQ;
- clasificación de solicitudes;
- respuestas;
- derivación;
- seguimiento.

---

# 21. Roadmap consolidado

## Urgente

1. estabilizar `SBM-API` y `DP-API`;
2. implementar QA y seguridad;
3. integrar `SBM-AI-ASSISTANT` con APIs;
4. comenzar AI-3016;
5. preparar Azure DevOps.

## Corto plazo

1. Azure Boards Agent;
2. Notion Documentation Agent;
3. Jira Business Agent;
4. observabilidad LLM;
5. evaluación;
6. Celery Beat;
7. MCP inicial.

## Mediano plazo

1. LangGraph;
2. múltiples proveedores;
3. OpenClaw como gateway opcional;
4. agentes especializados;
5. integración con marketplaces;
6. RAG avanzado;
7. memoria controlada.

## Largo plazo

1. multiagente;
2. marketing automatizado;
3. finanzas;
4. contabilidad;
5. operaciones;
6. empresa autónoma supervisada.

---

# 22. Criterio de finalización

Una capacidad de IA se considera implementada cuando:

1. resuelve un caso de negocio real;
2. tiene pruebas;
3. tiene permisos definidos;
4. tiene trazabilidad;
5. tiene evaluación;
6. tiene manejo de errores;
7. tiene documentación;
8. tiene observabilidad;
9. tiene controles de seguridad;
10. puede demostrarse en el portafolio.

---

# 23. Named agent/application model — 2026-08-16

`SBM-AI-ASSISTANT` remains the reasoning/tool/agent orchestrator. The canonical named-agent catalog is governed by `CEO Agent`, `SBM Agent` and `CFO Agent`, with specialized cells such as Development (`Tesla`, `Edison`, `Igor`, `Armstrong`), Security (`Batman`, `Alfred`, `Robin`, `Gotham`, `Joker`, `Queen`, `Darth Maul`, `Cerberus`, `Hercules`), Marketing/Content (`Belfort`, `Stratton`, `Donnie`, `DaVinci`, `Medici`) and brand agents (`DP`, `KS`, `PC`, `CG`). `Scrum Agent` owns backlog/process coordination. Legacy generic placeholders such as dev-agent, qa-agent, backlog-agent, marketing-agent and content-agent are superseded by these canonical named roles.

Domain applications keep persistent state and UI ownership: `SBM-AI-MANAGER`, `SBM-SECURITY`, `SBM-MARKETING`, `SBM-CONTENT`, `SBM-CONTROL`. Agents act through authorized APIs/tools and never acquire direct database authority; deterministic APIs, jobs and services remain the default execution path and agents activate only when reasoning is required.
