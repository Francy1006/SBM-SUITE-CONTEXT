# 🎓 Study Roadmap-NotebookLM

> Documento maestro de estudio para **Applied AI Engineering**, arquitectura, cloud, DevOps, Machine Learning y desarrollo empresarial aplicado a SBM Suite.
> 
> 
> Este archivo está diseñado para utilizarse como **fuente principal de un notebook en NotebookLM**. No es una lista aleatoria de tecnologías: organiza el aprendizaje por dependencias, resultados verificables, fuentes oficiales, evidencia para portafolio y criterios de avance.
> 
> **Última revisión:** julio de 2026
> 
> **Objetivo profesional:** Applied AI Engineer / AI Solutions Engineer / Senior Software Engineer
> 
> **Proyecto conductor:** SBM Suite
> 

---

# 1. Cómo utilizar esta página en NotebookLM

## Nombre recomendado del notebook

```
SBM Suite — Applied AI Study Roadmap
```

## Fuente principal

- `Study-Roadmap-NotebookLM.md`

## Fuentes internas complementarias

Cargar también:

1. `Development-Roadmap.md`
2. `Technologies-and-Tools.md`
3. `AI-Engineering.md`
4. `Machine-Learning-and-Deep-Learning.md`
5. `QA-and-Testing.md`
6. `Security-and-DevSecOps.md`
7. `DevOps-and-Platform-Engineering.md`
8. `Observability-and-Monitoring.md`
9. `Automation-and-Integration.md`
10. `Cloud-and-Infrastructure.md`
11. `Commerce-Stores-and-Marketplaces.md`
12. `Agentic-Enterprise-Operating-Model.md`
13. `Certifications-Tables.md`
14. `PROJECT_CONTEXT.md`
15. README de cada repositorio SBM.

## Regla de uso

NotebookLM debe tratar este archivo como:

- orden oficial de estudio;
- mapa de dependencias;
- fuente de prioridades;
- índice de referencias;
- criterio para generar planes semanales;
- base para cuestionarios;
- base para guías de entrevista;
- base para audios y resúmenes.

No debe alterar las prioridades sin explicarlo.

---

# 2. Prompt maestro para NotebookLM

```
Usa Study-Roadmap-NotebookLM.md como fuente principal y el resto de
los documentos como fuentes de apoyo.

Respeta el orden de dependencias definido en el roadmap.

Cuando generes un plan:
- no actives más de dos áreas principales por semana;
- prioriza implementación real en SBM Suite;
- utiliza primero las fuentes oficiales enlazadas;
- indica qué fuente respalda cada actividad;
- incluye objetivo, teoría, práctica, evidencia y criterio de término;
- no agregues tecnologías fuera de las fuentes sin marcarlas como sugerencia;
- diferencia claramente conocimiento obligatorio, recomendado y opcional;
- evita repetir contenido ya dominado por un desarrollador senior;
- relaciona cada tema con una funcionalidad concreta del portafolio.
```

---

# 3. Perfil objetivo

```
Senior Full Stack Developer
          +
Applied AI Engineer
          +
AI Solutions Engineer
          +
Software Architect
          +
Platform / DevOps Engineer
```

## Capacidades finales esperadas

- diseñar aplicaciones LLM;
- implementar RAG;
- crear agentes con tools;
- integrar APIs empresariales;
- evaluar calidad y seguridad;
- construir soluciones de Machine Learning;
- desplegar servicios en cloud;
- operar contenedores y Kubernetes;
- implementar CI/CD;
- diseñar arquitecturas escalables;
- explicar decisiones técnicas en entrevistas.

---

# 4. Proyecto conductor: SBM Suite

Toda área debe aplicarse en al menos uno de estos componentes:

| Proyecto | Stack | Uso formativo |
| --- | --- | --- |
| `SBM-MANAGER` | Vue.js | Administración interna |
| `SBM-API` | Django REST | API interna y arquitectura empresarial |
| `DP-API` | Django REST | API cliente y comercio |
| `SBM-DB` | PostgreSQL + Flyway | Datos, migraciones y arquitectura |
| `SBM-AI-ASSISTANT` | FastAPI + Qdrant + LLM | RAG, agentes y tools |
| `sbm-comercial` | React + TypeScript | Portal comercial |
| `KS-STORE` | React + TypeScript | E-commerce |
| `sbm-digital-api` | NestJS | BFF y canales digitales |
| Infraestructura | Docker, Jenkins, Azure, K3s | DevOps y Platform Engineering |

---

# 5. Orden real de dependencias

```
Base de software estable
        ↓
Testing y seguridad
        ↓
LLM + RAG
        ↓
Tool calling
        ↓
Agentes y LangGraph
        ↓
Evaluación y observabilidad
        ↓
Azure AI
        ↓
Machine Learning
        ↓
MLOps
        ↓
Kubernetes
        ↓
Data Engineering
        ↓
Arquitectura avanzada
```

## Regla

No avanzar a autonomía multiagente antes de contar con:

- APIs estables;
- permisos;
- pruebas;
- auditoría;
- tools deterministas;
- human approval;
- observabilidad.

---

# 6. Fase 0 — Preparación y línea base

## Objetivo

Preparar el entorno y medir el punto inicial.

## Temas

- inventario de repositorios;
- estado de documentación;
- dependencias;
- pruebas existentes;
- cobertura;
- seguridad;
- arquitectura actual;
- backlog;
- prioridades.

## Recursos oficiales

- [Git documentation](https://git-scm.com/doc)
- [Docker documentation](https://docs.docker.com/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [Python documentation](https://docs.python.org/3/)
- [Django documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## Actividades

1. actualizar `PROJECT_CONTEXT.md`;
2. actualizar README;
3. inventariar endpoints;
4. identificar duplicaciones;
5. documentar deuda técnica;
6. medir cobertura;
7. ejecutar escaneo inicial;
8. registrar arquitectura actual.

## Evidencia

- diagrama;
- inventario;
- backlog;
- baseline de cobertura;
- baseline de seguridad;
- documentación actualizada.

## Criterio de término

- todos los repositorios tienen contexto;
- se conoce el estado real de pruebas;
- se conoce el estado real de seguridad;
- existe un backlog priorizado.

---

# 7. Fase 1 — Backend, arquitectura y contratos

## Objetivo

Estabilizar la separación entre `SBM-API` y `DP-API`.

## Conocimientos obligatorios

- diseño REST;
- serializers;
- DTOs;
- validación;
- autenticación;
- autorización;
- OpenAPI;
- idempotencia;
- errores;
- arquitectura hexagonal;
- SOLID;
- integración entre servicios.

## Recursos oficiales

- [Django documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [HTTP Semantics — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [Martin Fowler — Hexagonal Architecture reference collection](https://martinfowler.com/architecture/)

## Proyecto aplicado

### Estabilización de `Product` y `Material`

- modelos;
- serializers;
- endpoints;
- validación;
- permisos;
- pruebas;
- documentación.

## Entregables

- `GET /api/products`;
- `POST /api/products`;
- contratos OpenAPI;
- tests;
- manejo de errores;
- ADR sobre separación de responsabilidades.

## Criterio de término

- los endpoints funcionan;
- no existe escritura directa indebida;
- los contratos están documentados;
- hay pruebas unitarias y de integración.

---

# 8. Fase 2 — QA y Testing

## Objetivo

Construir una red de seguridad para todo el desarrollo posterior.

## Conocimientos obligatorios

- pirámide de pruebas;
- unit testing;
- integration testing;
- API testing;
- contract testing;
- E2E;
- fixtures;
- mocks;
- coverage;
- mutation testing como etapa posterior.

## Recursos oficiales

- [pytest documentation](https://docs.pytest.org/)
- [Django testing tools](https://docs.djangoproject.com/en/stable/topics/testing/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Playwright documentation](https://playwright.dev/docs/intro)
- [Vitest documentation](https://vitest.dev/)
- [SonarQube documentation](https://docs.sonarsource.com/sonarqube-server/)
- [Schemathesis documentation](https://schemathesis.readthedocs.io/)

## Proyecto aplicado

Crear suites de prueba para:

- `SBM-API`;
- `DP-API`;
- `SBM-AI-ASSISTANT`;
- `SBM-MANAGER`;
- `sbm-comercial`.

## Entregables

- tests unitarios;
- tests de integración;
- tests de contratos;
- E2E crítico;
- cobertura en pipeline;
- Quality Gate.

## Criterio de término

- funcionalidades críticas tienen pruebas;
- el pipeline falla cuando las pruebas fallan;
- la cobertura está visible;
- los contratos API se validan automáticamente.

---

# 9. Fase 3 — Security y DevSecOps

## Objetivo

Integrar seguridad desde el pipeline.

## Conocimientos obligatorios

- OWASP Top 10;
- OWASP API Security;
- secret management;
- dependency scanning;
- SAST;
- DAST;
- container scanning;
- threat modeling;
- secure headers;
- RBAC;
- supply-chain security.

## Recursos oficiales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [Bandit documentation](https://bandit.readthedocs.io/)
- [Trivy documentation](https://trivy.dev/latest/docs/)
- [Gitleaks documentation](https://gitleaks.io/)
- [OWASP ZAP documentation](https://www.zaproxy.org/docs/)
- [MITRE ATT&CK](https://attack.mitre.org/)

## Proyecto aplicado

Pipeline DevSecOps:

```
Commit
  ↓
Lint
  ↓
Tests
  ↓
SAST
  ↓
Dependency Scan
  ↓
Secret Scan
  ↓
Container Scan
  ↓
DAST
  ↓
Report
```

## Evidencia

- reporte inicial;
- vulnerabilidades corregidas;
- políticas;
- escaneo automático;
- threat model.

## Criterio de término

- no existen secretos en repositorios;
- las imágenes se escanean;
- los findings críticos bloquean el pipeline;
- existe documentación de remediación.

---

# 10. Fase 4 — Fundamentos de aplicaciones LLM

## Objetivo

Comprender y aplicar los bloques básicos de una aplicación generativa.

## Conocimientos obligatorios

- tokens;
- context window;
- system prompts;
- temperature;
- structured output;
- JSON schema;
- streaming;
- retries;
- model providers;
- latency;
- cost;
- safety.

## Recursos oficiales

- [Microsoft Foundry documentation](https://learn.microsoft.com/azure/foundry/)
- [OpenAI API documentation](https://platform.openai.com/docs/)
- [Anthropic documentation](https://docs.anthropic.com/)
- [Cohere documentation](https://docs.cohere.com/)
- [Ollama documentation](https://docs.ollama.com/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)

## Proyecto aplicado

Refactor de `SBM-AI-ASSISTANT`:

- settings centralizados;
- prompts separados;
- schemas Pydantic;
- proveedor intercambiable;
- errores;
- logs;
- structured output.

## Entregables

- adapter de modelos;
- schemas;
- prompt registry;
- configuración por entorno;
- tests de respuestas estructuradas.

## Criterio de término

- el proveedor puede cambiarse;
- los outputs se validan;
- los errores tienen fallback;
- los prompts están versionados.

---

# 11. Fase 5 — RAG

## Objetivo

Construir recuperación documental confiable y medible.

## Conocimientos obligatorios

- embeddings;
- chunking;
- metadata;
- vector search;
- cosine similarity;
- filters;
- retrieval;
- reranking;
- citations;
- access control;
- evaluation.

## Recursos oficiales

- [Qdrant documentation](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://sbert.net/)
- [LangChain retrieval documentation](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Microsoft Foundry IQ and knowledge documentation](https://learn.microsoft.com/azure/foundry/)
- [Ragas documentation](https://docs.ragas.io/)
- [DeepEval documentation](https://deepeval.com/docs/)

## Ruta de aprendizaje

### Nivel 1

- ingestión;
- embeddings;
- chunks;
- retrieval básico;
- respuesta con contexto.

### Nivel 2

- metadata;
- filtros;
- versionado;
- incremental sync;
- citations;
- permisos.

### Nivel 3

- hybrid retrieval;
- reranking;
- query rewriting;
- evaluación;
- protección contra prompt injection indirecta.

## Proyecto aplicado

Mejorar RAG de Confluence:

- dataset de preguntas;
- evaluación;
- citas;
- filtros;
- permisos;
- comparación de chunking.

## Criterio de término

- existe un dataset de evaluación;
- se mide precisión de recuperación;
- la respuesta cita la fuente;
- el contenido inactivo no se recupera;
- los permisos son respetados.

---

# 12. Fase 6 — Tool Calling e integración de APIs

## Objetivo

Permitir que el asistente consulte y ejecute funciones empresariales.

## Conocimientos obligatorios

- function calling;
- JSON schemas;
- tool descriptions;
- validation;
- retries;
- timeouts;
- idempotency;
- permissions;
- human approval;
- error handling.

## Recursos oficiales

- [Microsoft Foundry tools overview](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/)

## Proyecto aplicado

### SBM API Integration Tool

Tools iniciales:

- consultar productos;
- consultar materiales;
- consultar servicios;
- consultar precios;
- consultar clientes;
- crear borrador de tarea;
- consultar estado.

## Entregables

- schemas;
- permissions;
- tests;
- audit;
- fallback;
- demo por Slack.

## Criterio de término

- la selección de tool es correcta;
- una tool inválida no se ejecuta;
- la entrada se valida;
- las acciones sensibles requieren aprobación;
- toda llamada queda auditada.

---

# 13. Fase 7 — Agentes y LangGraph

## Objetivo

Construir flujos de agentes controlados, persistentes y observables.

## Conocimientos obligatorios

- agents vs workflows;
- state;
- nodes;
- edges;
- routing;
- durable execution;
- memory;
- interrupts;
- human-in-the-loop;
- persistence;
- fallback.

## Recursos oficiales

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Microsoft Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/)

## Orden de implementación

1. deterministic workflow;
2. intent router;
3. tool router;
4. state;
5. approval interrupt;
6. persistence;
7. retries;
8. agent registry;
9. multi-agent workflow;
10. event-driven execution.

## Proyecto aplicado

```
Slack Request
      ↓
Intent Router
      ↓
Policy Layer
      ↓
LangGraph
      ↓
API Tool
      ↓
Approval when required
      ↓
Audit
      ↓
Response
```

## Criterio de término

- el flujo puede reanudarse;
- los estados son visibles;
- existe aprobación humana;
- los errores se manejan;
- no hay autonomía sin límites.

---

# 14. Fase 8 — Evaluación y observabilidad de IA

## Objetivo

Medir calidad, costo, seguridad y comportamiento.

## Métricas

- answer correctness;
- groundedness;
- retrieval relevance;
- hallucination rate;
- tool success;
- tool selection;
- latency;
- token usage;
- cost;
- escalation rate.

## Recursos oficiales

- [LangSmith documentation](https://docs.langchain.com/langsmith/)
- [Langfuse documentation](https://langfuse.com/docs)
- [Ragas](https://docs.ragas.io/)
- [DeepEval](https://deepeval.com/docs/)
- [Promptfoo](https://www.promptfoo.dev/docs/)
- [MLflow GenAI documentation](https://mlflow.org/docs/latest/genai/)

## Proyecto aplicado

- dataset de regresión;
- trazas;
- evaluación automática;
- dashboard;
- comparación Cohere/Ollama/Azure;
- detección de regresiones.

## Criterio de término

- se pueden comparar modelos;
- existe evaluación antes de release;
- se registran costos y latencia;
- los cambios de prompt se prueban.

---

# 15. Fase 9 — Seguridad LLM y agentes

## Objetivo

Reducir riesgos propios de aplicaciones generativas.

## Conocimientos obligatorios

- prompt injection;
- indirect prompt injection;
- tool abuse;
- excessive agency;
- sensitive data exposure;
- memory poisoning;
- insecure output handling;
- denial of service;
- cross-brand leakage.

## Recursos oficiales

- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- [Microsoft AI security documentation](https://learn.microsoft.com/security/ai/)
- [Garak documentation](https://reference.garak.ai/)
- [Promptfoo red teaming](https://www.promptfoo.dev/docs/red-team/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Proyecto aplicado

- red-team suite;
- tool allowlist;
- permission scopes;
- prompt injection tests;
- data leakage tests;
- human approval;
- incident runbook.

## Criterio de término

- existe suite de ataques;
- las tools están limitadas;
- los datos se separan por marca;
- las acciones críticas no son autónomas.

---

# 16. Fase 10 — Microsoft Foundry y Azure AI

## Objetivo

Aplicar IA en una plataforma enterprise.

## Recursos oficiales principales

- [Microsoft Foundry documentation](https://learn.microsoft.com/azure/foundry/)
- [Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/)
- [Foundry tools](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)
- [Azure Machine Learning](https://learn.microsoft.com/azure/machine-learning/)
- [Microsoft Learn AI hub](https://learn.microsoft.com/training/ai/)
- [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure free account](https://azure.microsoft.com/free/)

## Ruta

1. proyecto Foundry;
2. modelo;
3. SDK;
4. chat;
5. agent;
6. tool;
7. evaluation;
8. tracing;
9. security;
10. deployment.

## Proyecto aplicado

Migrar o agregar un proveedor Azure a `SBM-AI-ASSISTANT`.

## Evidencia

- arquitectura;
- modelo desplegado;
- tool;
- agent;
- logs;
- costos;
- evaluación;
- comparación con local.

## Criterio de término

- existe una demo funcional;
- se conocen costos;
- existe control de acceso;
- la implementación puede apagarse sin afectar la arquitectura general.

---

# 17. Fase 11 — Machine Learning

## Objetivo

Dominar ML clásico y construir un caso predictivo real.

## Conocimientos obligatorios

- data cleaning;
- exploratory analysis;
- feature engineering;
- train/validation/test;
- regression;
- classification;
- trees;
- Random Forest;
- gradient boosting;
- XGBoost;
- metrics;
- explainability;
- leakage;
- time series.

## Recursos oficiales

- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Pandas documentation](https://pandas.pydata.org/docs/)
- [NumPy documentation](https://numpy.org/doc/)
- [XGBoost documentation](https://xgboost.readthedocs.io/)
- [Kaggle Learn](https://www.kaggle.com/learn)
- [SHAP documentation](https://shap.readthedocs.io/)

## Proyecto aplicado

### Demand Forecasting

- dataset de ventas;
- baseline;
- features;
- validación temporal;
- modelo;
- explicación;
- API;
- dashboard.

## Criterio de término

- existe baseline;
- no hay leakage;
- se documentan métricas;
- el modelo supera el baseline;
- la predicción se sirve mediante API.

---

# 18. Fase 12 — Deep Learning

## Objetivo

Construir fundamentos prácticos de redes neuronales.

## Orden

1. tensores;
2. redes densas;
3. activaciones;
4. backpropagation;
5. optimización;
6. regularización;
7. CNN;
8. transfer learning;
9. transformers;
10. model serving.

## Recursos oficiales

- [PyTorch tutorials](https://pytorch.org/tutorials/)
- [TensorFlow tutorials](https://www.tensorflow.org/tutorials)
- [Keras guides](https://keras.io/guides/)
- [Hugging Face course](https://huggingface.co/learn)
- [OpenCV documentation](https://docs.opencv.org/)

## Proyecto aplicado

Elegir uno:

- OCR documental;
- clasificación de facturas;
- clasificación de fotografías;
- detección de elementos;
- clasificación de tickets.

## Criterio de término

- dataset separado;
- modelo entrenado;
- métricas;
- inferencia;
- error analysis;
- API;
- documentación.

---

# 19. Fase 13 — MLOps

## Objetivo

Operar modelos de forma reproducible.

## Conocimientos obligatorios

- experiment tracking;
- model registry;
- dataset versioning;
- reproducibility;
- serving;
- monitoring;
- drift;
- retraining;
- rollback.

## Recursos oficiales

- [MLflow documentation](https://mlflow.org/docs/latest/)
- [DVC documentation](https://dvc.org/doc)
- [Evidently AI documentation](https://docs.evidentlyai.com/)
- [ONNX documentation](https://onnx.ai/)
- [BentoML documentation](https://docs.bentoml.com/)

## Proyecto aplicado

```
Dataset
   ↓
Training
   ↓
MLflow
   ↓
Registry
   ↓
Validation
   ↓
API
   ↓
Monitoring
```

## Criterio de término

- el entrenamiento es reproducible;
- el modelo está versionado;
- existe rollback;
- se monitorean datos y predicciones.

---

# 20. Fase 14 — Redis, Celery y eventos

## Objetivo

Desacoplar procesos lentos y preparar arquitectura event-driven.

## Recursos oficiales

- [Redis documentation](https://redis.io/docs/latest/)
- [Celery documentation](https://docs.celeryq.dev/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [AsyncAPI specification](https://www.asyncapi.com/docs/reference/specification/latest)
- [Confluent Developer](https://developer.confluent.io/)

## Orden

1. Redis;
2. Celery;
3. retries;
4. idempotency;
5. Celery Beat;
6. outbox;
7. Kafka;
8. schemas;
9. observability.

## Proyecto aplicado

- sincronización Confluence;
- procesamiento de documentos;
- creación asíncrona de productos;
- notificaciones;
- eventos de stock y pedidos.

## Criterio de término

- los procesos lentos no bloquean APIs;
- existen retries;
- las tareas son idempotentes;
- se monitorean colas y fallos.

---

# 21. Fase 15 — Kubernetes y Platform Engineering

## Objetivo

Desplegar y operar SBM Suite en Kubernetes.

## Recursos oficiales

- [Kubernetes concepts](https://kubernetes.io/docs/concepts/)
- [Kubernetes tutorials](https://kubernetes.io/docs/tutorials/)
- [Helm documentation](https://helm.sh/docs/)
- [K3s documentation](https://docs.k3s.io/)
- [k3d documentation](https://k3d.io/)
- [CNCF Landscape](https://landscape.cncf.io/)

## Orden

1. pods;
2. deployments;
3. services;
4. ingress;
5. ConfigMaps;
6. Secrets;
7. probes;
8. resources;
9. Helm;
10. namespaces;
11. RBAC;
12. Network Policies;
13. storage;
14. observability.

## Proyecto aplicado

Desplegar:

- `SBM-API`;
- `DP-API`;
- `SBM-AI-ASSISTANT`;
- Redis;
- Qdrant;
- Prometheus;
- Grafana.

## Criterio de término

- despliegue reproducible;
- Helm;
- probes;
- límites de recursos;
- ingress;
- logs y métricas;
- seguridad básica.

---

# 22. Fase 16 — Observabilidad

## Objetivo

Tener visibilidad end-to-end.

## Recursos oficiales

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Prometheus documentation](https://prometheus.io/docs/)
- [Grafana documentation](https://grafana.com/docs/)
- [Loki documentation](https://grafana.com/docs/loki/latest/)
- [Tempo documentation](https://grafana.com/docs/tempo/latest/)
- [Sentry documentation](https://docs.sentry.io/)

## Señales

- logs;
- metrics;
- traces;
- errors;
- user events;
- LLM traces;
- queue metrics;
- infrastructure metrics.

## Proyecto aplicado

Trazar:

```
Frontend
  ↓
API
  ↓
Celery
  ↓
Database
  ↓
LLM
```

## Criterio de término

- existe correlation ID;
- se visualizan métricas;
- hay alertas;
- una falla puede seguirse entre servicios.

---

# 23. Fase 17 — Cloud e infraestructura

## Objetivo

Construir experiencia híbrida entre local, Azure y AWS.

## Azure

- [Azure Architecture Center](https://learn.microsoft.com/azure/architecture/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
- [Azure DevOps documentation](https://learn.microsoft.com/azure/devops/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)

## AWS

- [AWS documentation](https://docs.aws.amazon.com/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)
- [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/)

## Infrastructure as Code

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Ansible documentation](https://docs.ansible.com/)

## Proyecto aplicado

- Azure DevOps para repositorios, Boards y pipelines;
- servicio público pequeño en AWS;
- infraestructura local en K3s;
- Terraform para recursos reproducibles.

## Criterio de término

- arquitectura documentada;
- costos controlados;
- IaC;
- seguridad;
- monitoreo;
- estrategia de respaldo.

---

# 24. Fase 18 — Data Engineering

## Objetivo

Construir pipelines confiables para analítica y ML.

## Recursos oficiales

- [Apache Airflow documentation](https://airflow.apache.org/docs/)
- [dbt documentation](https://docs.getdbt.com/)
- [Apache Spark documentation](https://spark.apache.org/docs/latest/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Parquet documentation](https://parquet.apache.org/docs/)
- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)

## Proyecto aplicado

Pipeline de ventas:

```
PostgreSQL
   ↓
Extraction
   ↓
Validation
   ↓
Transformation
   ↓
Analytics Dataset
   ↓
Dashboard / ML
```

## Criterio de término

- datos versionados;
- calidad;
- lineage;
- ejecución repetible;
- dataset consumible por ML.

---

# 25. Fase 19 — React, comercio y canales digitales

## Objetivo

Construir una tienda propia con API propia y servicios desacoplados.

## Recursos oficiales

- [React documentation](https://react.dev/)
- [TypeScript documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS documentation](https://tailwindcss.com/docs)
- [NestJS documentation](https://docs.nestjs.com/)
- [Mercado Pago Developers](https://www.mercadopago.com/developers/)
- [Stripe documentation](https://docs.stripe.com/)
- [Mercado Libre Developers](https://developers.mercadolibre.com/)
- [Cloudinary documentation](https://cloudinary.com/documentation)
- [Google Search documentation](https://developers.google.com/search/docs)

## Proyecto aplicado

### `KS-STORE`

```
React Store
    ↓
sbm-digital-api
    ↓
DP-API
    ↓
PostgreSQL
```

## Funciones

- catálogo;
- variantes;
- carrito;
- checkout;
- pedidos;
- Mercado Pago;
- adaptador Stripe futuro;
- Mercado Libre como canal;
- SEO;
- analytics;
- Cloudinary.

## Criterio de término

- flujo de compra funcional;
- pagos desacoplados;
- webhooks validados;
- SEO técnico;
- pruebas E2E;
- Lighthouse documentado.

---

# 26. Fase 20 — Arquitectura avanzada y System Design

## Objetivo

Poder diseñar y explicar sistemas empresariales complejos.

## Temas

- DDD;
- bounded contexts;
- modular monolith;
- microservices;
- event-driven architecture;
- CQRS;
- outbox;
- saga;
- BFF;
- caching;
- consistency;
- availability;
- scalability;
- resilience.

## Recursos de referencia

- [Azure Architecture Center](https://learn.microsoft.com/azure/architecture/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [Martin Fowler](https://martinfowler.com/)
- [microservices.io](https://microservices.io/)
- [The Twelve-Factor App](https://12factor.net/)
- [Cloud Design Patterns](https://learn.microsoft.com/azure/architecture/patterns/)

## Prácticas

Diseñar:

- e-commerce;
- agent platform;
- marketplace integration;
- notification service;
- file processing;
- analytics platform;
- multi-brand ERP.

## Criterio de término

- puede explicar trade-offs;
- documenta ADRs;
- identifica fallos;
- propone escalamiento;
- considera seguridad y costos.

---

# 27. Ruta de certificaciones integrada

| Etapa | Credencial | Proyecto asociado |
| --- | --- | --- |
| 1 | Microsoft Applied Skill de GenAI | `SBM-AI-ASSISTANT` |
| 2 | Microsoft Applied Skill de agentes | API Integration Agent |
| 3 | Kaggle ML | Demand Forecasting |
| 4 | Kaggle Time Series | Forecasting |
| 5 | Azure AI Apps and Agents | Foundry Agent |
| 6 | CKAD | APIs sobre Kubernetes |
| 7 | Terraform Associate | Infraestructura híbrida |
| 8 | AWS AI Practitioner | Bedrock demo |
| 9 | AWS Solutions Architect Associate | Arquitectura pública |
| 10 | PyTorch Associate | Modelo Deep Learning |

Fuente de detalle: `Certifications-Tables.md`.

---

# 28. Roadmap de 24 semanas

## Bloque 1 — Base profesional

| Semana | Tema principal | Resultado |
| --- | --- | --- |
| 1 | Inventario y documentación | Contexto actualizado |
| 2 | Separación de APIs | Responsabilidades claras |
| 3 | Testing backend | Suite inicial |
| 4 | DevSecOps | Pipeline de seguridad |

## Bloque 2 — IA aplicada

| Semana | Tema principal | Resultado |
| --- | --- | --- |
| 5 | Structured output | Schemas y validación |
| 6 | RAG evaluation | Dataset y métricas |
| 7 | Tool calling | Tool de productos |
| 8 | Intent Router | Routing validado |
| 9 | LangGraph | Workflow con estado |
| 10 | Human approval | Acción protegida |
| 11 | LLM observability | Trazas y evaluación |
| 12 | AI security | Red-team suite |

## Bloque 3 — Azure y agentes

| Semana | Tema principal | Resultado |
| --- | --- | --- |
| 13 | Foundry fundamentals | Proyecto y modelo |
| 14 | Foundry Agent | Agente desplegado |
| 15 | Agent tools | API integrada |
| 16 | Applied Skill | Credencial y demo |

## Bloque 4 — ML y plataforma

| Semana | Tema principal | Resultado |
| --- | --- | --- |
| 17 | ML baseline | Dataset y baseline |
| 18 | Time series | Forecasting |
| 19 | MLflow | Experimentos |
| 20 | Redis + Celery | Procesamiento async |
| 21 | Kubernetes basics | Primer deployment |
| 22 | Helm | Despliegue reproducible |
| 23 | Observability | Dashboard |
| 24 | Portfolio release | Video y documentación |

---

# 29. Plan semanal generado por NotebookLM

Usar este prompt:

```
Genera el plan de la próxima semana usando exclusivamente las fuentes
del notebook.

Contexto:
- Perfil: Applied AI Engineer con base Senior Full Stack.
- Proyecto conductor: SBM Suite.
- Máximo: dos áreas principales.
- Disponibilidad semanal: [INDICAR HORAS].
- Estado actual: [INDICAR ESTADO].

Incluye:
1. objetivo semanal;
2. dependencias;
3. lecturas oficiales con enlaces;
4. ejercicios;
5. implementación en SBM Suite;
6. entregable;
7. evidencia para portafolio;
8. preguntas de entrevista;
9. criterio de finalización;
10. riesgos de desviación.

No incluyas tareas genéricas ni tecnologías que no estén justificadas.
```

---

# 30. Prompt para guía de estudio por tema

```
Crea una guía de estudio sobre [TEMA].

Usa únicamente las fuentes cargadas y prioriza documentación oficial.

Estructura:
- definición;
- problema que resuelve;
- conceptos previos;
- conceptos fundamentales;
- ejemplo mínimo;
- aplicación en SBM Suite;
- errores frecuentes;
- preguntas de entrevista;
- ejercicio práctico;
- criterio de dominio;
- enlaces utilizados.
```

---

# 31. Prompt para cuestionario

```
Genera un cuestionario de 20 preguntas sobre [TEMA]:

- 5 conceptuales;
- 5 de implementación;
- 5 de arquitectura;
- 3 de debugging;
- 2 de entrevista senior.

No entregues las respuestas inmediatamente.
Después de que responda, evalúa:
- precisión;
- profundidad;
- errores;
- brechas;
- siguiente actividad recomendada.
```

---

# 32. Prompt para preparación de entrevista

```
Actúa como entrevistador técnico para un rol de Applied AI Engineer.

Usa SBM Suite como contexto.

Evalúa:
- Python;
- APIs;
- RAG;
- agentes;
- tool calling;
- Machine Learning;
- Azure;
- Docker;
- Kubernetes;
- arquitectura;
- seguridad.

Haz una pregunta a la vez.
Después de cada respuesta:
- indica qué estuvo bien;
- corrige errores;
- entrega una respuesta senior mejorada;
- asigna una nota de 1 a 5.
```

---

# 33. Prompt para Audio Overview

```
Genera un Audio Overview que explique el roadmap como una conversación
entre un arquitecto de software y un ingeniero de IA.

Prioriza:
- orden de dependencias;
- por qué no empezar con multiagentes;
- relación entre APIs, RAG, tools y agentes;
- proyecto de forecasting;
- Azure y Kubernetes;
- evidencia de portafolio.

Evita enumerar herramientas sin contexto.
```

---

# 34. Prompt para Flashcards

```
Genera flashcards de [TEMA].

Formato:
Pregunta | Respuesta breve | Ejemplo SBM Suite | Error frecuente

Incluye solo conceptos importantes para:
- implementación;
- arquitectura;
- entrevistas.
```

---

# 35. Fuentes internas que deben mantenerse actualizadas

| Fuente | Frecuencia |
| --- | --- |
| `PROJECT_CONTEXT.md` | Después de cambios importantes |
| README de repositorios | Por release |
| `Development-Roadmap.md` | Mensual |
| `Technologies-and-Tools.md` | Trimestral |
| `Certifications-Tables.md` | Trimestral |
| `Study-Roadmap-NotebookLM.md` | Mensual |
| ADRs | Por decisión |
| OpenAPI | Automática |
| Diagramas | Por cambio arquitectónico |

---

# 36. Sistema de evidencia

## Por cada tema estudiado

Registrar:

- fecha;
- fuente;
- resumen;
- ejercicio;
- implementación;
- commit;
- captura;
- métrica;
- problema encontrado;
- solución;
- pregunta de entrevista.

## Formato recomendado

```
Topic:
Official source:
What I learned:
What I implemented:
Repository:
Commit:
Evidence:
Error found:
How I solved it:
Interview explanation:
Next step:
```

---

# 37. Definición de dominio

Un tema se considera dominado cuando:

1. se puede explicar sin leer;
2. se puede implementar;
3. se puede depurar;
4. se puede probar;
5. se puede integrar;
6. se puede documentar;
7. se conocen sus límites;
8. se pueden comparar alternativas;
9. se puede responder en entrevista;
10. existe evidencia real.

---

# 38. Anti-patrones de estudio

No hacer:

- cursos sin proyecto;
- cinco rutas simultáneas;
- copiar tutoriales sin comprender;
- estudiar herramientas sin problema real;
- empezar multiagentes sin tools estables;
- implementar Kubernetes antes de dominar contenedores;
- entrenar modelos sin baseline;
- publicar modelos sin evaluación;
- acumular certificados básicos;
- ignorar documentación oficial;
- usar NotebookLM como única fuente de verdad.

---

# 39. Revisión mensual

NotebookLM debe generar un informe mensual usando este prompt:

```
Analiza el avance del último mes usando el roadmap y las evidencias.

Entrega:
- objetivos completados;
- objetivos incompletos;
- conocimiento adquirido;
- evidencia creada;
- certificaciones avanzadas;
- brechas;
- deuda técnica;
- prioridades del próximo mes;
- temas que deben eliminarse o postergarse;
- porcentaje estimado de avance por fase.

No evalúes solo cantidad de horas: evalúa resultados verificables.
```

---

# 40. Prioridad actual

## Urgente

1. estabilizar `SBM-API` y `DP-API`;
2. crear pruebas;
3. implementar pipeline de seguridad;
4. completar primera Applied Skill de Microsoft;
5. integrar una tool real en `SBM-AI-ASSISTANT`;
6. implementar Intent Router;
7. documentar la arquitectura.

## Corto plazo

1. LangGraph;
2. human approval;
3. evaluación RAG;
4. Langfuse o alternativa;
5. Redis;
6. Celery;
7. Machine Learning baseline.

## Mediano plazo

1. Microsoft Foundry;
2. Kafka;
3. Kubernetes;
4. observabilidad;
5. forecasting;
6. MLOps;
7. `KS-STORE`.

## Largo plazo

1. AWS;
2. Deep Learning;
3. computer vision;
4. múltiples agentes;
5. automatización empresarial;
6. arquitectura multi-cloud.

---

# 41. Criterio de finalización del roadmap

El roadmap se considera exitoso cuando existe evidencia pública y explicable de:

- aplicación RAG;
- agente con tools;
- human approval;
- evaluación de IA;
- seguridad LLM;
- modelo ML;
- pipeline MLOps;
- despliegue cloud;
- Kubernetes;
- CI/CD;
- observabilidad;
- arquitectura documentada;
- e-commerce funcional;
- certificaciones verificables.

---

# 42. Visión final

```
Official Learning Sources
          +
NotebookLM Study System
          +
SBM Suite Implementation
          +
Public Evidence
          +
Certifications
          +
Interview Readiness
```

Este roadmap funciona como el **índice maestro de aprendizaje**. NotebookLM debe utilizarlo para transformar documentación oficial y contexto del proyecto en planes, cuestionarios, resúmenes y materiales de estudio, mientras SBM Suite funciona como el laboratorio práctico donde cada conocimiento se demuestra.