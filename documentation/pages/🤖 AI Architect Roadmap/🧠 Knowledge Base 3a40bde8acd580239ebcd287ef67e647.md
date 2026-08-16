# 🧠 Knowledge Base

> Arquitectura de conocimiento para SBM Suite.
> 
> 
> Esta página define cómo organizar, mantener, consultar y conectar la documentación técnica, operativa y estratégica del ecosistema SBM.
> 
> El objetivo es evitar información duplicada, dispersa o desactualizada, y construir una base de conocimiento útil para humanos, agentes IA, NotebookLM, RAG, onboarding, desarrollo y operación.
> 

---

# 1. Objetivo

Construir una Knowledge Base capaz de:

- centralizar conocimiento;
- separar documentación por propósito;
- mantener una fuente oficial por tema;
- evitar duplicación;
- facilitar onboarding;
- alimentar RAG;
- alimentar NotebookLM;
- permitir búsqueda semántica;
- soportar agentes IA;
- registrar decisiones;
- documentar arquitectura;
- mantener contexto de proyectos;
- mejorar continuidad entre conversaciones;
- permitir auditoría y actualización.

---

# 2. Principios

1. **Single source of truth**
    
    Cada tema debe tener una fuente principal claramente definida.
    
2. **Right tool for the right knowledge**
    
    No toda documentación debe vivir en la misma plataforma.
    
3. **No uncontrolled duplication**
    
    Si una información se replica, debe indicar cuál es la fuente oficial.
    
4. **Versioned knowledge**
    
    Las decisiones técnicas deben quedar versionadas.
    
5. **Project-local context**
    
    Cada repositorio debe contener su propia documentación esencial.
    
6. **Enterprise-level context**
    
    La visión transversal debe vivir fuera de repositorios individuales.
    
7. **Human and AI readable**
    
    La documentación debe ser clara para personas y modelos.
    
8. **Searchable knowledge**
    
    El contenido debe poder recuperarse por búsqueda textual y semántica.
    
9. **Access control**
    
    El conocimiento sensible debe respetar permisos.
    
10. **Continuous maintenance**
    
    La documentación se actualiza como parte del desarrollo.
    

---

# 3. Arquitectura general

```
Knowledge Sources
      │
      ├── Notion
      ├── Obsidian
      ├── NotebookLM
      ├── Confluence
      ├── Azure DevOps Wiki
      ├── README
      ├── PROJECT_CONTEXT.md
      ├── ADRs
      ├── OpenAPI
      ├── Diagrams
      └── Repositories
      │
      ▼
Knowledge Governance
      │
      ├── Ownership
      ├── Versioning
      ├── Status
      ├── Review
      ├── Permissions
      └── Source of Truth
      │
      ▼
Knowledge Consumption
      │
      ├── Humans
      ├── NotebookLM
      ├── RAG
      ├── Agents
      ├── Onboarding
      └── Audits
```

---

# 4. Herramientas y propósito

| Herramienta | Uso principal | Fuente oficial |
| --- | --- | --- |
| Notion | Visión, roadmaps, estrategia, planificación | Sí, para visión transversal |
| Obsidian | Notas personales y conocimiento técnico | No siempre |
| NotebookLM | Estudio asistido sobre fuentes cargadas | No |
| Confluence | Documentación empresarial operativa | Sí, para procesos internos |
| Azure DevOps Wiki | Documentación técnica empresarial | Sí, para operación técnica |
| README | Uso e instalación por repositorio | Sí, para cada repo |
| `PROJECT_CONTEXT.md` | Memoria persistente para IA | Sí, para contexto técnico |
| ADRs | Decisiones de arquitectura | Sí |
| OpenAPI | Contratos de APIs | Sí |
| DBML | Modelo de datos | Sí |
| Diagramas | Arquitectura y flujos | Sí, si están versionados |
| GitHub / Repos | Código y documentación cercana al código | Sí |

---

# 5. Clasificación del conocimiento

## Estratégico

Incluye:

- visión;
- objetivos;
- prioridades;
- roadmap;
- carrera;
- certificaciones;
- arquitectura futura.

### Ubicación principal

- Notion.

---

## Técnico

Incluye:

- arquitectura;
- APIs;
- modelos;
- infraestructura;
- decisiones;
- pipelines;
- seguridad;
- despliegues.

### Ubicación principal

- repositorios;
- Azure DevOps Wiki;
- ADRs;
- README;
- `PROJECT_CONTEXT.md`.

---

## Operativo

Incluye:

- procedimientos;
- manuales;
- checklists;
- soporte;
- permisos;
- tareas;
- procesos internos.

### Ubicación principal

- Confluence;
- Azure DevOps Wiki;
- SBM Suite.

---

## Académico

Incluye:

- notas;
- resúmenes;
- conceptos;
- cursos;
- papers;
- ejercicios;
- flashcards.

### Ubicación principal

- Obsidian;
- NotebookLM.

---

## Evidencia

Incluye:

- demos;
- capturas;
- métricas;
- certificados;
- videos;
- reportes;
- resultados.

### Ubicación principal

- repositorios;
- Notion;
- LinkedIn;
- portafolio.

---

# 6. Notion

## Rol

Notion será la capa de visión y planificación transversal.

## Contenido recomendado

- SBM Suite;
- Development Roadmap;
- Technologies & Tools;
- AI Engineering;
- Security;
- Cloud;
- Commerce;
- Marketing;
- Finance;
- Operations;
- Certifications;
- Study Roadmap;
- Career Roadmap;
- Knowledge Base;
- Job Search.

## No debe contener

- secretos;
- configuraciones sensibles;
- código fuente completo;
- logs;
- detalles operativos que ya tienen fuente oficial;
- documentación duplicada sin referencia.

---

# 7. Obsidian

## Rol

Base personal de conocimiento técnico.

## Casos

- conceptos;
- notas de cursos;
- resúmenes;
- snippets;
- preguntas de entrevista;
- aprendizaje;
- relaciones entre temas;
- diarios técnicos.

## Estructura sugerida

```
Obsidian Vault
├── 00-Inbox
├── 01-AI
├── 02-Machine-Learning
├── 03-Architecture
├── 04-Backend
├── 05-Frontend
├── 06-DevOps
├── 07-Cloud
├── 08-Security
├── 09-Data
├── 10-Interview
├── 11-Certifications
├── 12-SBM-Suite
└── 99-Archive
```

## Regla

Obsidian sirve para aprender y conectar ideas, no como fuente empresarial oficial.

---

# 8. NotebookLM

## Rol

Sistema de estudio y síntesis basado en fuentes.

## Usos

- planes semanales;
- resúmenes;
- cuestionarios;
- flashcards;
- mapas mentales;
- Audio Overviews;
- preparación de entrevistas;
- comparación de documentos;
- detección de brechas.

## Fuente principal recomendada

- `Study-Roadmap-NotebookLM.md`.

## Fuentes complementarias

- páginas Notion exportadas;
- documentación oficial;
- README;
- `PROJECT_CONTEXT.md`;
- documentación técnica;
- certificaciones.

## Regla

NotebookLM no es la fuente oficial. Interpreta fuentes existentes.

---

# 9. Confluence

## Rol

Documentación empresarial y operativa.

## Contenido

- procesos;
- manuales;
- procedimientos;
- onboarding;
- políticas;
- preguntas frecuentes;
- operaciones;
- soporte;
- documentación de negocio.

## Integración actual

`SBM-AI-ASSISTANT` consume contenido desde Confluence para RAG.

## Requisitos

- versionado;
- permisos;
- exclusiones;
- metadata;
- estado activo;
- sync incremental;
- trazabilidad.

---

# 10. Azure DevOps Wiki

## Rol

Documentación técnica empresarial.

## Contenido

- arquitectura;
- entornos;
- CI/CD;
- runbooks;
- operaciones;
- incidentes;
- decisiones;
- despliegues;
- integraciones;
- troubleshooting.

## Ventaja

Queda cerca de:

- Repos;
- Boards;
- Pipelines;
- Releases;
- Work Items.

---

# 11. README

## Rol

Documento de entrada por repositorio.

## Debe contener

- propósito;
- stack;
- arquitectura;
- requisitos;
- instalación;
- configuración;
- ejecución;
- pruebas;
- endpoints;
- seguridad;
- despliegue;
- troubleshooting;
- roadmap;
- enlaces.

## Regla

El README no debe intentar reemplazar toda la documentación del sistema.

---

# 12. PROJECT_CONTEXT.md

## Rol

Memoria técnica persistente para IA.

## Debe contener

- objetivo;
- estado real;
- arquitectura;
- decisiones;
- componentes;
- endpoints;
- problemas conocidos;
- roadmap;
- convenciones;
- restricciones;
- historial relevante.

## Debe evitar

- secretos;
- contraseñas;
- tokens;
- datos personales;
- afirmaciones no verificadas;
- contenido genérico.

## Regla

Debe actualizarse después de cambios importantes.

---

# 13. Architecture Decision Records

## Rol

Registrar decisiones técnicas relevantes.

## Template

```
# ADR-0001 — Title

Status:
Date:
Context:
Decision:
Alternatives:
Consequences:
Risks:
Related systems:
```

## Casos

- Django vs FastAPI;
- monolito modular vs microservicios;
- Qdrant;
- Kafka;
- Redis;
- Azure;
- AWS;
- Kubernetes;
- payment adapters;
- OpenClaw;
- MCP;
- LangGraph.

---

# 14. OpenAPI

## Rol

Contrato oficial de APIs.

## Debe definir

- endpoints;
- métodos;
- schemas;
- errores;
- auth;
- ejemplos;
- estados;
- paginación;
- filtros;
- versionado.

## Regla

No documentar endpoints manualmente si OpenAPI puede generarlos.

---

# 15. Modelos de datos

## Fuentes oficiales

- DBML;
- migraciones;
- modelos Django;
- schemas;
- diagramas ER.

## Prioridad

```
Migration
  ↓
Model
  ↓
DBML
  ↓
Documentation
```

## Regla

La documentación debe reflejar el estado real del esquema.

---

# 16. Diagramas

## Tipos

- contexto;
- contenedores;
- componentes;
- secuencia;
- despliegue;
- datos;
- flujos;
- eventos;
- agentes.

## Herramientas

- Mermaid;
- PlantUML;
- draw.io;
- Excalidraw;
- Figma;
- DBML.

## Regla

Preferir diagramas como código cuando sea posible.

---

# 17. Taxonomía

## Metadata mínima

Cada documento debe indicar:

- título;
- dominio;
- sistema;
- marca;
- owner;
- estado;
- versión;
- fecha;
- fuente oficial;
- sensibilidad;
- tags.

## Ejemplo

```
Domain: AI
System: SBM-AI-ASSISTANT
Owner: Technology
Status: Active
Version: 2.1
Source of Truth: Yes
Sensitivity: Internal
Tags: rag, qdrant, confluence
```

---

# 18. Estados de documentación

```
draft
review
approved
active
deprecated
archived
```

## Regla

El contenido deprecated debe señalar su reemplazo.

---

# 19. Ownership

## Cada documento debe tener

- owner;
- reviewer;
- fecha de última revisión;
- próxima revisión;
- sistema relacionado.

## Ejemplo

| Documento | Owner | Revisión |
| --- | --- | --- |
| `PROJECT_CONTEXT.md` | Tech Lead | Por cambio importante |
| README | Repo owner | Por release |
| ADR | Architecture | Permanente |
| Runbook | Operations | Trimestral |
| Study Roadmap | Owner personal | Mensual |

---

# 20. Source of Truth Matrix

| Tema | Fuente oficial |
| --- | --- |
| Visión de producto | Notion |
| Estado técnico | `PROJECT_CONTEXT.md` |
| Instalación | README |
| Contrato API | OpenAPI |
| Modelo de datos | Migraciones + DBML |
| Decisiones | ADRs |
| Operación | Azure Wiki / Confluence |
| Procesos de negocio | Confluence |
| Estudio | Study Roadmap |
| Certificaciones | Certifications Tables |
| Carrera | Career Roadmap |
| Código | Repositorio |
| Infraestructura | IaC + Wiki |

---

# 21. Regla anti-duplicación

Antes de crear documentación:

1. buscar si ya existe;
2. identificar la fuente oficial;
3. decidir si se debe actualizar;
4. enlazar en lugar de copiar;
5. copiar solo si existe una razón;
6. indicar la fuente;
7. definir owner.

## Ejemplo correcto

```
El contrato oficial está disponible en OpenAPI.
Ver: /docs
```

## Ejemplo incorrecto

Copiar manualmente todos los endpoints en cinco documentos diferentes.

---

# 22. Estrategia de enlaces

## Enlaces internos

Cada página debe enlazar:

- sistema relacionado;
- repositorio;
- ADR;
- OpenAPI;
- documentación;
- roadmap;
- evidencias.

## Regla

Usar enlaces relativos cuando la documentación vive en Git.

---

# 23. Knowledge Graph

## Objetivo

Conectar entidades y conceptos.

## Relaciones

```
Project
  ├── Repository
  ├── API
  ├── Database
  ├── ADR
  ├── Agent
  ├── Documentation
  ├── Owner
  └── Deployment
```

## Uso

- búsqueda;
- navegación;
- RAG;
- impacto de cambios;
- onboarding;
- agentes.

---

# 24. RAG Architecture

```
Knowledge Sources
      ↓
Ingestion
      ↓
Normalization
      ↓
Chunking
      ↓
Metadata
      ↓
Embeddings
      ↓
Qdrant
      ↓
Retrieval
      ↓
LLM
      ↓
Cited Answer
```

---

# 25. Ingestion Sources

## Iniciales

- Confluence;
- README;
- documentación Markdown;
- Azure Wiki;
- Notion exportado;
- PDFs internos;
- OpenAPI;
- ADRs.

## Futuros

- Git repositories;
- tickets;
- incidentes;
- dashboards;
- runbooks;
- documentación externa autorizada.

---

# 26. Chunking

## Estrategia

El chunking debe depender del tipo de documento.

| Documento | Estrategia |
| --- | --- |
| Manual | Por sección |
| README | Por heading |
| ADR | Documento completo |
| OpenAPI | Por endpoint |
| FAQ | Por pregunta |
| Runbook | Por procedimiento |
| Política | Por regla |
| Tabla | Mantener contexto |

## Regla

No cortar arbitrariamente información que pierde sentido.

---

# 27. Metadata RAG

## Campos

- source;
- document_id;
- title;
- section;
- domain;
- system;
- brand;
- version;
- status;
- permissions;
- created_at;
- updated_at;
- is_active;
- source_url.

---

# 28. Access Control

## Objetivo

Evitar recuperación de contenido no autorizado.

## Controles

- permisos por usuario;
- permisos por rol;
- marca;
- dominio;
- documento;
- nivel de sensibilidad;
- filtros en retrieval;
- logs.

## Regla

El control de acceso debe ocurrir antes de entregar contexto al LLM.

---

# 29. Citations

## Requisito

Toda respuesta RAG debe indicar:

- documento;
- sección;
- URL;
- versión cuando corresponda.

## Objetivo

- trazabilidad;
- validación;
- confianza;
- auditoría.

---

# 30. Knowledge Quality

## Métricas

- freshness;
- completeness;
- duplication;
- broken links;
- ownership;
- retrieval success;
- citation coverage;
- outdated documents;
- unanswered questions.

---

# 31. Knowledge Review

## Frecuencia

| Contenido | Revisión |
| --- | --- |
| Roadmaps | Mensual |
| README | Por release |
| ADRs | No se reescriben; se reemplazan |
| Runbooks | Trimestral |
| Políticas | Semestral |
| Arquitectura | Por cambio |
| Certificaciones | Trimestral |
| Study Roadmap | Mensual |
| Career Roadmap | Mensual |

---

# 32. Documentation as Code

## Objetivo

Mantener documentación técnica junto al código.

## Elementos

- Markdown;
- Mermaid;
- ADRs;
- OpenAPI;
- DBML;
- scripts;
- CI validation.

## Validaciones

- links;
- headings;
- spelling;
- schemas;
- diagrams;
- formatting.

---

# 33. Automation

## Casos

- generar OpenAPI;
- detectar documentación obsoleta;
- revisar links;
- actualizar índices;
- sincronizar Confluence;
- crear embeddings;
- versionar chunks;
- crear resúmenes;
- generar changelog;
- notificar owner.

## Herramientas

- CI/CD;
- n8n;
- Celery;
- agentes;
- scripts;
- MCP.

---

# 34. Documentation Agent

## Responsabilidades futuras

- detectar cambios;
- proponer actualizaciones;
- generar resúmenes;
- crear borradores;
- vincular documentación;
- detectar duplicación;
- actualizar índices;
- identificar contenido obsoleto.

## Límites

- no publicar cambios críticos sin revisión;
- no eliminar documentación;
- no inventar estado;
- no marcar algo como oficial sin owner.

---

# 35. Notion Documentation Agent

## Responsabilidades

- crear páginas;
- actualizar roadmaps;
- sincronizar tablas;
- generar reportes;
- organizar contenido;
- mantener enlaces.

## Requisitos

- permisos limitados;
- templates;
- audit;
- aprobación;
- versionado.

---

# 36. Obsidian MCP

## Objetivo

Permitir acceso controlado a notas personales.

## Casos

- búsqueda;
- creación de notas;
- resumen;
- links;
- actualización;
- clasificación.

## Regla

No mezclar automáticamente notas personales con documentación oficial.

---

# 37. Azure DevOps Documentation Agent

## Responsabilidades

- actualizar Wiki;
- crear documentación desde work items;
- generar release notes;
- documentar pipelines;
- crear runbooks;
- vincular PRs y ADRs.

---

# 38. NotebookLM Workflow

```
Official Sources
      ↓
NotebookLM
      ↓
Study Guide
      ↓
Quiz
      ↓
Audio Overview
      ↓
Personal Notes
      ↓
Applied Project
```

## Regla

Los resultados generados deben distinguirse de las fuentes.

---

# 39. Onboarding Knowledge Pack

## Contenido

- visión;
- arquitectura;
- sistemas;
- repositorios;
- entornos;
- convenciones;
- procesos;
- seguridad;
- despliegue;
- roadmap;
- contactos.

## Formato

- página principal;
- checklist;
- enlaces;
- videos;
- diagramas;
- FAQ.

---

# 40. Incident Knowledge

## Contenido

- descripción;
- impacto;
- causa;
- timeline;
- resolución;
- acciones;
- prevención;
- owner.

## Ubicación

- Azure Wiki;
- repositorio;
- sistema de incidentes.

---

# 41. Runbooks

## Casos

- despliegue;
- rollback;
- restauración;
- rotación de secretos;
- caída de API;
- colas;
- base de datos;
- Kubernetes;
- certificados;
- incidentes IA.

## Template

```
Purpose
Preconditions
Steps
Validation
Rollback
Escalation
Owner
```

---

# 42. Troubleshooting

## Estructura

```
Symptom
Possible cause
How to verify
Resolution
Prevention
Related issue
```

---

# 43. Change Log

## Debe registrar

- cambio;
- sistema;
- versión;
- fecha;
- autor;
- impacto;
- documentación asociada.

## Fuentes

- Git tags;
- releases;
- PRs;
- Azure Boards;
- pipelines.

---

# 44. Knowledge Security

## Clasificación

```
public
internal
confidential
restricted
```

## Controles

- permisos;
- cifrado;
- auditoría;
- retención;
- eliminación;
- masking;
- secretos fuera de documentación.

---

# 45. Backup

## Fuentes críticas

- Notion exports;
- Obsidian vault;
- Confluence exports;
- Wiki;
- repositories;
- NAS;
- cloud backup.

## Regla

La Knowledge Base también debe seguir una estrategia 3-2-1.

---

# 46. Search Experience

## Tipos

- búsqueda textual;
- filtros;
- búsqueda semántica;
- navegación;
- relaciones;
- historial;
- recomendaciones.

## Futuro

- búsqueda unificada;
- citations;
- permisos;
- feedback;
- analytics.

---

# 47. Knowledge Analytics

## Métricas

- búsquedas;
- consultas sin respuesta;
- documentos más usados;
- documentos obsoletos;
- errores;
- fuentes;
- usuarios;
- tiempo de resolución;
- feedback.

---

# 48. Roadmap de implementación

## Etapa 1 — Organización

1. definir fuentes oficiales;
2. normalizar nombres;
3. organizar Notion;
4. organizar repositorios;
5. actualizar README;
6. actualizar `PROJECT_CONTEXT.md`.

## Etapa 2 — Gobierno

1. owners;
2. estados;
3. metadata;
4. revisión;
5. taxonomía;
6. source of truth matrix.

## Etapa 3 — Automatización

1. sync Confluence;
2. validación de links;
3. indexación;
4. embeddings;
5. citations;
6. alertas.

## Etapa 4 — Agentes

1. Documentation Agent;
2. Notion Agent;
3. Azure Wiki Agent;
4. Obsidian MCP;
5. knowledge analytics.

## Etapa 5 — Enterprise Knowledge Platform

1. búsqueda unificada;
2. permisos;
3. graph;
4. feedback;
5. observabilidad;
6. lifecycle management.

---

# 49. Prioridad actual

## Urgente

1. mantener Notion como visión;
2. usar README por repositorio;
3. actualizar `PROJECT_CONTEXT.md`;
4. crear ADRs;
5. definir source of truth;
6. preparar Study Roadmap para NotebookLM;
7. evitar duplicaciones.

## Corto plazo

1. organizar Obsidian;
2. crear Azure Wiki;
3. mejorar RAG;
4. agregar citations;
5. documentar APIs;
6. definir metadata.

## Mediano plazo

1. Documentation Agent;
2. Notion Agent;
3. Obsidian MCP;
4. búsqueda unificada;
5. knowledge analytics.

---

# 50. Criterio de finalización

La Knowledge Base se considera madura cuando:

1. cada tema tiene fuente oficial;
2. cada documento tiene owner;
3. la documentación está versionada;
4. existen enlaces;
5. se evita duplicación;
6. los permisos funcionan;
7. RAG entrega citas;
8. NotebookLM usa fuentes confiables;
9. los repositorios están documentados;
10. existe revisión periódica;
11. existe backup;
12. el conocimiento puede encontrarse rápidamente.

---

# 51. Visión final

```
Structured Knowledge
        +
Clear Ownership
        +
Versioned Documentation
        +
Semantic Search
        +
RAG
        +
AI Agents
        +
Human Governance
```

SBM Suite debe evolucionar hacia una plataforma donde el conocimiento técnico, operativo y estratégico sea reutilizable, verificable, seguro y accesible tanto para personas como para agentes IA.