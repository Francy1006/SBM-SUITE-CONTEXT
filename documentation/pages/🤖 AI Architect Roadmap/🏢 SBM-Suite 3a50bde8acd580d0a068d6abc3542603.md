# 🏢 SBM-Suite

> **Last updated:** 2026-08-13
>
> **Purpose:**
>
> Documentar la visión, arquitectura, componentes, estado operativo y roadmap de SBM Suite como plataforma empresarial multimarca y AI-native.
>
> **Source of truth:**
>
> `SBM-SUITE/context/PROJECT_CONTEXT.md`, `SBM-SUITE/context/QA_CONTEXT.md`, `SBM-SUITE/context/DATA_CONTEXT.md`, `SBM-SUITE/context/DECISIONS_CONTEXT.md` y los repositorios de proyecto validados.

## 1. Overview

> **AI-native, agent-orchestrated business operating system**
> 
> 
> SBM Suite es una plataforma empresarial multimarca, modular y omnicanal, diseñada para administrar distintas empresas desde un núcleo tecnológico común.
> 
> Su objetivo es centralizar operaciones, ventas, clientes, productos, documentos, automatizaciones, analítica, marketing, finanzas, contabilidad y canales digitales, utilizando aplicaciones web, APIs, integraciones, Machine Learning y agentes de Inteligencia Artificial.
> 
> La visión final es permitir que distintas empresas operen con una estructura humana reducida, apoyada por agentes IA especializados, automatizaciones y controles de aprobación humana.
> 

---

### 1. Objetivo de SBM Suite

SBM Suite no es solamente un ERP ni una colección de aplicaciones independientes.

Es una plataforma para construir, operar y automatizar empresas mediante:

- un núcleo administrativo común;
- módulos empresariales reutilizables;
- una API interna transversal;
- APIs cliente por marca;
- aplicaciones administrativas y comerciales;
- tiendas y canales digitales;
- integraciones externas;
- automatización de procesos;
- agentes IA especializados;
- analítica y modelos predictivos;
- infraestructura, QA, seguridad y observabilidad.

La plataforma debe permitir incorporar nuevas marcas sin reconstruir toda la arquitectura.

---

## 2. Scope

### 3. Marcas administradas

| Marca | Descripción |
| --- | --- |
| Ditaly Pasta | Franquicia gastronómica de comida rápida especializada en pastas, con gestión de locales, franquiciados, ventas, pedidos, compras, documentos, permisos y planos. |
| Kiseki Tech | Empresa de importación y venta de artículos tecnológicos, con tienda online, costos en USD y operación mediante Mercado Libre. |
| Consorcio Gastronómico | Empresa de asesoría y tramitación de patentes comerciales, resoluciones sanitarias, documentación y planos. |
| PortalConvenios.cl | Plataforma de convenios de bienestar y salud para empresas y entidades públicas, con gestión de prestadores, clientes, operativos y agenda. |

Ditaly Pasta es actualmente la marca principal utilizada para el desarrollo funcional.

---

## 3. Current state

### 6. Estado actual del desarrollo

#### Foco funcional

Actualmente el desarrollo está concentrado en Ditaly Pasta.

Los módulos `product` y `material` fueron implementados recientemente en:

- `dp-api`;
- `sbm-manager`.

Antes de continuar con nuevos módulos de negocio, se implementará una base transversal de calidad y seguridad.

#### Separación entre `sbm-api` y `dp-api`

Actualmente `sbm-api` todavía contiene métodos y endpoints que corresponden a `dp-api`.

Se está ejecutando una migración para establecer responsabilidades definitivas.

##### Estado deseado

`sbm-api`:

- procesos internos;
- funciones críticas;
- administración SBM;
- lógica transversal;
- selección de marca o franquicia;
- operaciones no expuestas directamente al cliente.

`dp-api`:

- primera API cliente;
- productos;
- materiales;
- catálogos;
- precios públicos;
- pedidos;
- clientes;
- proveedores;
- sucursales;
- tickets;
- procesos públicos de Ditaly Pasta.

##### Resultado esperado

1. Eliminar de `sbm-api` las funciones que correspondan a `dp-api`.
2. Eliminar duplicaciones.
3. Establecer contratos claros entre ambas APIs.
4. Separar correctamente permisos y usuarios.
5. Preparar comunicación síncrona y asíncrona.
6. Documentar responsabilidades por servicio.

### 7. Estado validado de Context y Documentation

| Objective ID | Project | Objective | Status | Validation |
|---|---|---|---|---|
| OBJ-CTX-013 | SBM-SUITE | Corregir y validar el workflow de documentación de `SBM-SUITE/context`, incluyendo `documentation-deploy.sh`, `documentation-upgrade.sh` y el flujo completo posterior a `context-upgrade`. | completed | `implementation-closure` y `context-upgrade` completados; Context/Documentation quedaron centralizados bajo `SBM-SUITE/context`, Documentation opera globalmente y QA fue validado estructuralmente como `not-applicable` al no existir `scripts/qa-check.sh`. |
| OBJ-CTX-001 | SBM-SUITE | Validate and stabilize the expanded context governance model, synchronized section patches and project-tree evidence | completed | Lifecycle-only/no-op closure registrada el 2026-08-13; `implementation-closure` y `context-upgrade` completados. QA fue `not-applicable` porque `scripts/qa-check.sh` no existe para `sbm-suite-context`; no se acreditan cambios de implementación. |

---

## 4. Core concepts

### 2. Principios de arquitectura

1. **Multimarca**
    
    Una misma plataforma puede administrar distintas empresas, franquicias y unidades de negocio.
    
2. **Modular**
    
    Cada dominio empresarial debe evolucionar sin acoplar innecesariamente toda la plataforma.
    
3. **API-first**
    
    Las capacidades del negocio deben exponerse mediante contratos claros para ser utilizadas por aplicaciones, agentes e integraciones.
    
4. **Arquitectura híbrida**
    
    Los módulos de negocio utilizarán arquitectura hexagonal cuando exista lógica relevante. Los módulos genéricos podrán mantenerse con arquitectura por capas.
    
5. **Omnicanal**
    
    Los datos podrán distribuirse hacia tiendas propias, aplicaciones, marketplaces, redes sociales y canales presenciales.
    
6. **Event-driven**
    
    Los procesos distribuidos podrán comunicarse mediante eventos para reducir acoplamiento.
    
7. **AI-native**
    
    La Inteligencia Artificial será parte de la arquitectura y no solamente una interfaz de chat.
    
8. **Agent-orchestrated**
    
    Los agentes podrán consultar información, ejecutar herramientas y coordinar procesos según permisos definidos.
    
9. **Secure by design**
    
    QA, seguridad, trazabilidad y observabilidad se integrarán desde el ciclo de desarrollo.
    
10. **Human-in-the-loop**
    
    Las decisiones críticas, tributarias, financieras, legales o irreversibles requerirán aprobación humana.
    

---

## 5. Architecture or operating model

### 4. Modelo de APIs

#### `sbm-api`

API interna y transversal de SBM Suite.

Debe concentrar los procesos críticos y administrativos utilizados por los usuarios internos de SBM.

Responsabilidades generales:

- administración;
- configuración;
- franquicias y marcas;
- inventario central;
- cálculos;
- procesos fiscales;
- operaciones internas;
- finanzas;
- contabilidad;
- marketing;
- documentos;
- automatizaciones;
- integraciones internas;
- permisos y auditoría.

#### APIs cliente por marca

Cada marca podrá disponer de una API cliente cuando sus procesos públicos o comerciales lo requieran.

Estas APIs expondrán únicamente las funciones necesarias para:

- clientes finales;
- tiendas;
- aplicaciones públicas;
- marketplaces;
- portales;
- integraciones externas autorizadas.

##### Primera API cliente

`dp-api` es la primera API cliente de SBM Suite y corresponde a Ditaly Pasta.

Las futuras marcas podrán incorporar APIs propias cuando exista una necesidad funcional real.

---

### 5. Arquitectura general

```
                         SBM Suite

                   Usuarios internos
                          │
                          ▼
                    sbm-manager
                          │
                          ▼
                       sbm-api
                API interna transversal
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
     dp-api       futuras APIs cliente   sbm-ai-assistant
 Primera API                              IA, RAG, Tools,
 cliente                                  Agentes y MCP
        │
        └──────────────┐
                       ▼
                    sbm-db
             PostgreSQL / Flyway
       autoridad de esquemas y migraciones
```

Arquitectura futura ampliada:

```
Usuarios internos
       │
       ▼
sbm-manager
       │
       ▼
sbm-api
       │
       ├── sbm-ai-assistant
       ├── sbm-digital-api
       ├── dp-api
       ├── futuras APIs cliente
       ├── sbm-db
       ├── Kafka
       ├── Redis / Celery
       └── servicios externos

Usuarios públicos
       │
       ├── dp-store
       ├── sbm-comercial
       ├── futuras tiendas
       ├── aplicaciones móviles
       ├── marketplaces
       └── redes sociales
```

---

## 6. Components

### 7. Repositorios y aplicaciones

#### `sbm-manager`

##### Tipo

Frontend administrativo interno.

##### Propósito

Centralizar la administración de SBM Suite y de todas las marcas asociadas.

##### Funciones actuales y futuras

- productos;
- materiales;
- usuarios;
- marcas;
- inventario;
- precios;
- pedidos;
- proveedores;
- franquicias;
- operaciones;
- marketing;
- finanzas;
- contabilidad;
- documentos;
- automatizaciones;
- dashboards;
- configuración de agentes IA.

##### Tecnologías actuales

- Vue.js;
- JavaScript;
- Vue Router;
- Pinia;
- Axios;
- Docker.

##### Evolución planificada

- TypeScript;
- Vitest;
- Vue Test Utils;
- Playwright;
- SonarQube;
- seguridad frontend;
- accesibilidad;
- telemetría;
- módulos visuales;
- integración con contenidos y canales digitales.

##### Estado

🚧 En desarrollo.

#### `sbm-api`

##### Tipo

Backend interno transversal.

##### Propósito

Gestionar procesos críticos, administrativos y compartidos de SBM Suite.

##### Arquitectura

- arquitectura hexagonal en módulos con reglas de negocio;
- arquitectura por capas en módulos genéricos;
- adaptadores para servicios externos;
- comunicación mediante APIs y eventos.

##### Tecnologías actuales

- Django;
- Django REST Framework;
- PostgreSQL;
- Docker.

##### Evolución planificada

- pytest;
- pytest-django;
- pytest-cov;
- SonarQube;
- Redis;
- Celery;
- Kafka;
- OpenTelemetry;
- seguridad automatizada;
- contratos de integración.

##### Estado

🚧 En refactorización y separación de responsabilidades.

#### `dp-api`

##### Tipo

Primera API cliente de SBM Suite.

##### Propósito

Exponer los procesos públicos y comerciales de Ditaly Pasta.

##### Dominios actuales o planificados

- productos;
- materiales;
- catálogos;
- precios;
- clientes;
- pedidos;
- ventas;
- proveedores;
- sucursales;
- tickets;
- servicios;
- configuración pública de marca.

##### Tecnologías actuales

- Django;
- Django REST Framework;
- PostgreSQL;
- Docker.

##### Evolución planificada

- arquitectura hexagonal en módulos de negocio;
- pytest;
- pruebas de integración;
- contract testing;
- SonarQube;
- Kafka;
- Redis;
- Celery;
- OpenTelemetry.

##### Estado

🚧 En desarrollo.

#### Futuras APIs cliente

Cada nueva API deberá justificarse por una necesidad real de negocio.

Podrán aparecer cuando una marca necesite:

- contratos públicos propios;
- lógica comercial diferente;
- integración con marketplaces;
- aplicaciones especializadas;
- reglas de acceso particulares;
- escalamiento independiente.

No deben crearse anticipadamente sin necesidad funcional.

#### `sbm-ai-assistant`

##### Tipo

Orquestador de Inteligencia Artificial, herramientas, agentes y conocimiento empresarial.

##### Estado actual

Actualmente incluye:

- RAG documental;
- integración con Confluence;
- embeddings;
- Qdrant;
- Slack como interfaz;
- Cohere como LLM;
- sincronización programada;
- respuestas basadas en documentación empresarial.

##### Siguiente avance

Conectar `sbm-ai-assistant` con:

1. `sbm-api`;
2. `dp-api`.

Flujo objetivo:

```
Usuario
   │
   ▼
Slack / Chat / Web
   │
   ▼
sbm-ai-assistant
   │
   ├── detecta intención
   ├── valida permisos
   ├── selecciona Tool o Agent
   ├── consulta sbm-api o dp-api
   ├── procesa respuesta
   └── registra trazabilidad
```

##### Evolución planificada

- LangGraph;
- MCP;
- Azure AI Foundry;
- agentes especializados;
- herramientas empresariales;
- observabilidad LLM;
- evaluaciones;
- guardrails;
- aprobación humana;
- integración con Notion.

##### Estado

🚧 RAG implementado; integración con APIs como siguiente etapa.

#### `sbm-db`

##### Tipo

Repositorio central de persistencia y migraciones.

##### Tecnologías

- PostgreSQL;
- Flyway;
- DBML;
- dbdiagram.io;
- Docker.

##### Responsabilidades

- modelo de datos;
- esquemas;
- migraciones;
- integridad;
- versionado;
- scripts;
- configuración inicial;
- datos maestros.

##### Evolución planificada

- pruebas de migraciones;
- backups;
- restauración;
- auditoría;
- configuración digital por marca;
- datos de contacto por marca;
- dominios;
- correos;
- WhatsApp;
- redes sociales;
- SEO;
- configuraciones de tienda.

Estos datos de marca se incorporarán cuando comience formalmente la etapa de publicación de `dp-store`.

##### Estado

🚧 En desarrollo.

#### `dp-store`

##### Tipo

Primera tienda pública asociada a una marca.

##### Propósito

Servir como canal digital de Ditaly Pasta y como modelo reutilizable para futuras tiendas.

##### Funciones futuras

- catálogo;
- productos;
- imágenes;
- videos;
- promociones;
- contacto;
- WhatsApp;
- SEO;
- pedidos;
- configuración de marca;
- integración con redes sociales;
- conexión con la API cliente correspondiente.

##### Estado

📅 Planificado.

#### `sbm-comercial`

##### Tipo

Frontend React comercial y transversal.

##### Propósito

Servir como portal corporativo y comercial de SBM Suite.

Podrá consumir información de:

- `sbm-api`;
- `dp-api`;
- futuras APIs cliente;
- `sbm-digital-api`;
- servicios externos.

##### Tecnologías

- React;
- TypeScript;
- Tailwind CSS;
- React Router;
- TanStack Query;
- Vite;
- Docker.

##### Estado

🚧 Base existente / evolución funcional planificada.

#### `sbm-digital-api`

##### Tipo

Backend for Frontend y Digital Experience API.

##### Tecnología objetivo

- Node.js;
- NestJS;
- TypeScript.

##### Propósito

Unificar y adaptar información para canales públicos.

##### Responsabilidades

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
- integración con distintas APIs cliente;
- aislamiento de `sbm-api`.

##### Justificación

Esta API permite que `sbm-comercial`, `dp-store` y futuros canales consuman una capa especializada sin conectarse directamente a múltiples servicios internos.

##### Estado

📅 Planificado.

#### `nginx-proxy`

##### Tipo

Infraestructura de producción.

##### Responsabilidades

- reverse proxy;
- routing;
- publicación de aplicaciones;
- terminación HTTPS;
- protección básica.

##### Estado

✅ Implementado.

#### `cert-bot`

##### Tipo

Gestión de certificados TLS.

##### Responsabilidades

- emisión;
- renovación;
- integración con Let’s Encrypt.

En Kubernetes podrá complementarse o reemplazarse por `cert-manager`.

##### Estado

✅ Implementado.

#### Jenkins

##### Tipo

CI/CD.

##### Responsabilidades actuales y futuras

- construcción;
- pruebas;
- análisis;
- imágenes Docker;
- despliegues;
- validaciones;
- integración con SonarQube;
- escaneo de seguridad.

Azure DevOps también se incorporará como plataforma empresarial complementaria.

##### Estado

✅ Implementado parcialmente; ampliación planificada.

---

## 7. Workflows

### 16. Documentación y gestión

#### Notion

Contendrá:

- visión general;
- roadmap;
- tecnologías;
- certificaciones;
- prioridades;
- estado global.

La documentación técnica detallada se reducirá progresivamente a medida que migre hacia Azure DevOps y los repositorios.

#### Azure DevOps

Se utilizará para:

- Repos;
- Boards;
- Pipelines;
- Wiki;
- dashboards;
- QA;
- documentación técnica;
- seguimiento;
- evidencia empresarial.

#### GitHub

Se mantendrá como vitrina pública y portafolio.

#### README por repositorio

Cada repositorio tendrá documentación específica de:

- objetivo;
- arquitectura;
- instalación;
- configuración;
- variables;
- endpoints;
- pruebas;
- despliegue;
- integración.

---

## 8. Configuration

La configuración técnica permanece propiedad de cada repositorio y no se documentan valores secretos.

Para `SBM-DB`, la evidencia suministrada confirma:

- PostgreSQL como motor de base de datos;
- Flyway como autoridad de migraciones;
- `flyway.locations=filesystem:/flyway/sql` para el flujo `analytics`;
- `.sonar/` excluido del control de versiones;
- SonarQube configurado para analizar Shell/YAML/secrets, con Flyway SQL fuera del alcance de Community Build.

## 9. Security

La base transversal de seguridad continúa como trabajo planificado a nivel Suite.

### Seguridad

- SAST;
- DAST;
- dependencias;
- secretos;
- contenedores;
- Kubernetes;
- APIs;
- redes;
- seguridad LLM;
- auditoría.

## 10. Validation

La validación transversal descrita por el documento fuente contempla:

### QA

- pruebas unitarias;
- pruebas de integración;
- pruebas de contrato;
- pruebas E2E;
- cobertura;
- SonarQube;
- pruebas de carga;
- reportes automáticos.

### Evidencia actual de `SBM-DB`

La evidencia QA suministrada el `2026-08-08` registra:

- estado general `passed`;
- 33 migraciones validadas en `sbm_business`;
- 55 migraciones validadas en `ditaly_pasta`;
- 5 migraciones validadas en el flujo `cross`;
- 2 migraciones validadas en `analytics`;
- SonarQube Quality Gate `PASSED`;
- Flyway SQL fuera del análisis estático de SonarQube Community Build.

## 11. Known limitations

Limitaciones y transiciones explícitas en el documento fuente:

- `sbm-api` todavía contiene métodos y endpoints que corresponden a `dp-api`;
- la separación definitiva entre `sbm-api` y `dp-api` continúa en evolución;
- PostgreSQL podrá mantenerse inicialmente fuera del clúster para evitar complejidad innecesaria;
- varios servicios, agentes, canales y componentes de infraestructura permanecen planificados.

## 12. Roadmap

### Objetivos actuales de `SBM-MANAGER`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| SBM-MANAGER-001 | Integrar SBM-MANAGER completamente a SBM Suite, incluyendo contextos, lifecycle scripts, QA/SonarQube, registro en sbm-ai-assistant, sincronización global y actualización del diagrama canónico de arquitectura en SUITE_CONTEXT.md. | active | 5 | 2026-08-07 | `FEATURE-integrates-sbm-manager` |
| SBM-MANAGER-002 | Corregir SBM-MANAGER para consumir correctamente SBM-API y DP-API según ownership canónico. | active | 5 | N/A | `BUGFIX-corrects-api-ownership` |
| SBM-MANAGER-003 | Corregir y completar QA de SBM-MANAGER. | pending | 5 | N/A | `BUGFIX-completes-manager-qa` |

Estos objetivos permanecen **active/pending**. Su presencia en el roadmap representa planificación vigente y no acredita cierre ni implementación completada.

### Objetivo activo de `SBM-DB`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| SBM-DB-001 | habilitación de sbm-db | active | 5 | 2026-08-07 | `FEATURE-enables-sbm-db` |

Este objetivo permanece **active**. Su presencia aquí no representa cierre ni implementación completada.

### Objetivos actuales de `SBM-SUITE/context`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| OBJ-DOC-001 | Implement the manual documentation deploy and upgrade workflow with dedicated RAG and Qdrant collection | pending | 4 |  | FEATURE-adds-documentation-workflow |
| OBJ-CTX-002 | Habilitar un sistema automatizado para ejecutar flujos transversales sobre uno o varios proyectos. | pending | 5 | N/A | FEATURE-automates-cross-project-flows |
| OBJ-CTX-003 | Separar QA y Context mediante una estructura específica por proyecto. | pending | 5 | N/A | FEATURE-separates-qa-context |
| OBJ-CTX-004 | Habilitar un nuevo proyecto para procesamiento asíncrono, incluyendo PostgreSQL, Celery, Redis, Kafka y los componentes de infraestructura relacionados. | pending | 5 | N/A | FEATURE-enables-async-platform |
| OBJ-CTX-005 | Habilitar un proyecto UTIL para centralizar servicios y utilidades reutilizables y desacoplarlos de proyectos específicos, incluyendo generación de ZIP y procesamiento de contextos. | pending | 5 | N/A | FEATURE-enables-shared-utils |
| OBJ-CTX-006 | Habilitar un agente de backlog que convierta objetivos en issues y épicas y gestione su sincronización con Jira vía API. El nombre definitivo del agente se revisará al activar el objetivo. | pending | 5 | N/A | FEATURE-enables-backlog-agent |
| OBJ-CTX-007 | Habilitar un agente QA para gestionar y automatizar procesos de validación de calidad de los proyectos. | pending | 5 | N/A | FEATURE-enables-qa-agent |
| OBJ-CTX-008 | Habilitar un entorno y flujo de seguridad ejecutado después de QA y antes del commit. | pending | 5 | N/A | FEATURE-enables-security-flow |
| OBJ-CTX-009 | Habilitar un agente de seguridad para ejecutar y gestionar las validaciones del flujo de seguridad. | pending | 5 | N/A | FEATURE-enables-security-agent |
| OBJ-CTX-010 | Habilitar una aplicación para visualizar y gestionar agentes, definiendo la tecnología y lenguaje apropiados al activar el objetivo. | pending | 5 | N/A | FEATURE-enables-agent-management |
| OBJ-CTX-011 | Completar `INIT_CONTEXT.md` para soportar creación/onboarding de nuevos proyectos SBM. | pending | 5 | N/A | FEATURE-completes-project-onboarding |
| OBJ-CTX-012 | Separar el flujo del agente en `SBM_AGENT_INIT.md`, dejando `INIT_CONTEXT.md` como punto de entrada y orquestación. | pending | 5 | N/A | FEATURE-separates-agent-init-flow |
| OBJ-CTX-014 | Habilitar QA transversal en `SBM-SUITE/context` para ejecutar, centralizar y gestionar validaciones QA de los proyectos de la suite desde el contexto global, manteniendo los scripts QA específicos por proyecto y una orquestación común desde `context`. | pending | 5 | N/A | FEATURE-enables-transversal-qa |

Los objetivos anteriores conservan literalmente su estado operativo actual de Context. Los objetivos `active` y `pending` son planificación y no acreditan implementación completada.

### Objetivo pendiente de `SBM-DB`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| SBM-DB-002 | Actualizar SBM-DB al contrato lifecycle actual de Context, incluyendo objectives[], execution_mode, preservación literal de objetivos y paths relativos. | pending | 5 | N/A | FEATURE-updates-context-lifecycle |

Este objetivo permanece pending y se documenta únicamente como planificación.

### 8. Procesamiento asíncrono e integración

#### Redis

Se utilizará para:

- caché;
- broker de Celery;
- locks;
- datos temporales;
- control de concurrencia.

#### Celery

Se utilizará para:

- tareas en segundo plano;
- procesos pesados;
- reintentos;
- sincronizaciones;
- generación documental;
- correos;
- procesamiento de IA;
- integraciones externas.

#### Celery Beat

Se utilizará como scheduler distribuido.

La sincronización programada de Confluence en `sbm-ai-assistant` deberá migrarse desde APScheduler hacia Celery Beat cuando se implemente la infraestructura distribuida.

#### Kafka

Se utilizará como bus de eventos empresariales.

Ejemplos:

```
product.created
product.updated
order.created
inventory.updated
price.changed
document.approved
campaign.created
invoice.issued
appointment.scheduled
```

Kafka no reemplaza a Celery:

- Kafka comunica eventos entre servicios.
- Celery ejecuta tareas internas.

---

### 9. Infraestructura objetivo

```
Docker / Docker Compose
         │
         ▼
     k3d + K3s
         │
         ├── Helm
         ├── Ingress NGINX
         ├── cert-manager
         ├── Redis
         ├── Celery Workers
         ├── Celery Beat
         ├── Kafka KRaft
         ├── Kafka UI
         ├── Qdrant
         ├── n8n
         ├── Prometheus
         ├── Grafana
         ├── Loki
         ├── Tempo
         └── OpenTelemetry
```

PostgreSQL podrá mantenerse inicialmente fuera del clúster para evitar complejidad innecesaria.

---

### 10. Comercio y canales digitales

SBM Suite deberá permitir que las APIs cliente alimenten diferentes canales.

```
SBM Suite
├── tiendas propias
├── aplicaciones móviles
├── Mercado Libre
├── portales públicos
├── ventas presenciales
├── redes sociales
└── futuros marketplaces
```

#### Mercado Libre

La integración futura deberá contemplar:

- publicaciones;
- productos;
- precios;
- stock;
- pedidos;
- preguntas;
- despachos;
- comisiones;
- reputación;
- conciliación.

#### Tipo de cambio

Para negocios de importación, SBM Suite deberá:

- consultar el valor diario del USD;
- conservar historial;
- registrar la fuente;
- recalcular costos;
- generar precios sugeridos;
- aplicar márgenes;
- requerir aprobación antes de publicar cambios relevantes.

---

### 11. Multimedia, SEO y redes sociales

#### Multimedia

- Cloudinary;
- YouTube;
- imágenes optimizadas;
- videos embebidos;
- activos por marca;
- gestión centralizada de contenido.

#### SEO

- Google Search Console;
- Google Analytics;
- Google Tag Manager;
- Lighthouse;
- PageSpeed Insights;
- Schema.org;
- Open Graph;
- sitemap;
- robots.txt.

#### Redes sociales

Las publicaciones podrán gestionarse mediante:

- APIs oficiales;
- n8n;
- agentes IA;
- flujos de aprobación;
- calendarios editoriales.

Canales considerados:

- Instagram;
- Facebook;
- YouTube;
- LinkedIn;
- TikTok;
- WhatsApp.

---

### 12. Módulos futuros

Estos módulos forman parte de la visión completa, pero se implementarán después de estabilizar el núcleo técnico.

#### Marketing

- campañas;
- calendario editorial;
- promociones;
- segmentación;
- contenidos;
- redes sociales;
- métricas;
- automatización;
- Content Factory.
    - Figma;

Herramientas contempladas:

- Figma API;
- Photoshop;
- Illustrator;
- Premiere Pro;
- After Effects;
- Blender;
- DaVinci Resolve;
- ComfyUI;
- Cloudinary;
- n8n.

#### Operaciones

- locales;
- espacios;
- equipamiento;
- distribución;
- planos;
- permisos;
- versiones;
- aprobaciones;
- drag-and-drop;
- capas;
- medidas;
- exportación.

Tecnologías posibles:

- Vue Flow;
- React Flow;
- Konva.js;
- Fabric.js;
- Three.js;
- SVG;
- DXF;
- Blender;
- Figma.

#### Finanzas

- flujo de caja;
- ingresos;
- egresos;
- cuentas por cobrar;
- cuentas por pagar;
- presupuestos;
- centros de costo;
- conciliación;
- indicadores;
- proyecciones;
- rentabilidad;
- alertas.

#### Contabilidad e integración tributaria

SBM Suite utilizará una capa de adaptación hacia proveedores externos de facturación electrónica.

```
SBM Suite
    │
    ▼
Billing / Accounting Module
    │
    ▼
DTE Provider Adapter
    │
    ▼
Proveedor externo
    │
    ▼
SII
```

Esto permitirá:

- reducir riesgo ante cambios técnicos;
- cambiar de proveedor;
- mantener estable la lógica interna;
- aislar la integración tributaria.

---

### 13. Inteligencia Artificial y agentes

#### Arquitectura objetivo

```
Usuario
   │
   ▼
Slack / Chat / Web
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
   ├── Permission and Policy Layer
   ├── Audit and Observability
   └── Human Approval
```

#### Estado actual

Actualmente `sbm-ai-assistant` incluye:

- RAG documental;
- integración con Confluence;
- embeddings;
- Qdrant;
- Slack como interfaz;
- Cohere como LLM;
- sincronización programada;
- respuestas basadas en documentación empresarial.

La siguiente etapa consiste en conectar el asistente con las APIs de negocio de SBM Suite.

---

#### Orden de implementación de agentes e integraciones

##### 1. SBM API Integration Agent

Será la primera integración operativa de `sbm-ai-assistant`.

Responsabilidades:

- detectar la intención del usuario;
- determinar si corresponde consultar `sbm-api` o `dp-api`;
- consumir endpoints mediante tools controladas;
- validar autenticación, permisos, marca y alcance;
- transformar respuestas técnicas en respuestas conversacionales;
- registrar solicitudes, resultados y errores;
- comenzar con operaciones de solo lectura;
- incorporar acciones de escritura únicamente con confirmación y autorización;
- preparar la incorporación futura de nuevas APIs cliente por marca.

```
Usuario
   │
   ▼
sbm-ai-assistant
   │
   ▼
SBM API Integration Agent
   │
   ├── sbm-api
   └── dp-api
```

---

##### 2. Azure Boards Agent

Será el agente responsable del backlog técnico de SBM Suite.

Responsabilidades:

- consultar el backlog;
- crear Product Backlog Items;
- crear bugs y tareas;
- generar descripciones técnicas;
- generar criterios de aceptación;
- asignar prioridad;
- actualizar estados;
- relacionar tareas con repositorios;
- relacionar trabajo con commits, pull requests y pipelines;
- generar resúmenes del avance técnico.

Azure Boards será la fuente oficial del trabajo de desarrollo.

---

##### 3. Notion Documentation Agent

Permitirá actualizar la documentación general y el roadmap mediante conversación.

Responsabilidades:

- leer páginas autorizadas;
- actualizar estados;
- crear secciones;
- reorganizar contenido;
- registrar decisiones;
- modificar roadmaps;
- generar resúmenes;
- mantener trazabilidad;
- solicitar aprobación antes de cambios importantes.

Integración:

- Notion API;
- Notion MCP;
- permisos limitados;
- auditoría de cambios.

Notion continuará funcionando como documentación general, visión global, roadmap y seguimiento de aprendizaje.

---

##### 4. Jira Business Agent

Será responsable de las tareas operativas y de negocio, manteniéndolas separadas del backlog técnico.

Responsabilidades:

- crear tareas operativas;
- registrar solicitudes internas;
- gestionar requerimientos comerciales;
- registrar campañas;
- gestionar solicitudes de clientes;
- mantener seguimiento de procesos de negocio;
- actualizar estados y prioridades;
- generar resúmenes operativos.

Jira no será el backlog principal de desarrollo.

---

#### Flujo de gestión inicial

```
Usuario
   │
   ▼
sbm-ai-assistant
   │
   ├── SBM API Integration Agent
   │      ├── sbm-api
   │      └── dp-api
   │
   ├── Azure Boards Agent
   │      └── Backlog técnico
   │
   ├── Notion Documentation Agent
   │      └── Roadmap y documentación general
   │
   └── Jira Business Agent
          └── Tareas operativas y de negocio
```

---

#### Agentes especializados planificados

Después de implementar las integraciones prioritarias, se incorporarán progresivamente agentes especializados.

- Executive Assistant Agent;
- Documentation Agent;
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

#### Modelo de operación

Cada agente deberá disponer de:

- propósito claramente definido;
- tools autorizadas;
- permisos mínimos;
- acceso limitado por marca;
- validación de entradas;
- validación de resultados;
- trazabilidad;
- auditoría;
- límites de ejecución;
- aprobación humana para acciones críticas;
- manejo de errores y reintentos.

Los agentes no deberán acceder directamente a la base de datos ni ejecutar operaciones fuera de sus permisos.

---

#### Evolución futura

La evolución de `sbm-ai-assistant` incluirá:

- LangGraph;
- MCP;
- Azure AI Foundry;
- múltiples proveedores LLM;
- memoria controlada;
- observabilidad LLM;
- evaluación automática;
- guardrails;
- seguridad contra prompt injection;
- control de costos y tokens;
- human-in-the-loop;
- agentes especializados por área;
- coordinación de flujos multiagente.

### 14. Machine Learning y Deep Learning

Las capacidades de ML y DL se incorporarán cuando exista un caso de negocio concreto.

Casos potenciales:

- predicción de demanda;
- predicción de ventas;
- optimización de inventario;
- precios sugeridos;
- detección de anomalías;
- OCR;
- clasificación documental;
- recomendación de productos;
- segmentación de clientes;
- forecasting financiero;
- análisis de campañas.

El detalle se mantendrá en la página **Machine Learning & Deep Learning**.

---

Antes de continuar con nuevos módulos, SBM Suite implementará una base transversal.

### Observabilidad

- métricas;
- logs;
- trazas;
- dashboards;
- alertas;
- correlation IDs;
- health checks;
- monitoreo de Kafka;
- monitoreo de Celery;
- observabilidad LLM.

### 17. Prioridad inmediata

1. Finalizar la separación entre `sbm-api` y `dp-api`.
2. Eliminar endpoints y procesos duplicados.
3. Estabilizar `product` y `material`.
4. Implementar QA transversal.
5. Incorporar pruebas unitarias y de integración.
6. Integrar cobertura y SonarQube.
7. Incorporar herramientas de seguridad gratuitas o locales.
8. Documentar cada repositorio.
9. Migrar progresivamente la gestión a Azure DevOps.
10. Conectar `sbm-ai-assistant` con `sbm-api` y `dp-api`.
11. Implementar Redis y Celery.
12. Migrar el scheduler de IA a Celery Beat.
13. Incorporar Kafka.
14. Implementar Kubernetes.
15. Incorporar observabilidad.

---

### 18. Desarrollo posterior

1. `dp-store`.
2. Configuración digital por marca.
3. `sbm-digital-api`.
4. Futuras APIs cliente.
5. Comercio omnicanal.
6. Mercado Libre.
7. SEO y redes sociales.
8. Multimedia.
9. Machine Learning.
10. Agentes especializados.
11. Marketing.
12. Operaciones y planos.
13. Finanzas.
14. Contabilidad.
15. Integración tributaria.
16. Mayor autonomía empresarial.

---

### 19. Formación paralela

El desarrollo avanzará en paralelo con certificaciones y formación técnica.

#### Prioridad urgente

**AI-3016: Develop generative AI apps in Azure AI Foundry portal**

Objetivos:

- crear el entorno Microsoft;
- completar el contenido;
- obtener la credencial;
- aprender Azure AI Foundry;
- utilizar Azure DevOps Free;
- aplicar posteriormente lo aprendido en `sbm-ai-assistant` y SBM Suite.

---

### 20. Visión final

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

SBM Suite busca convertirse en un **sistema operativo empresarial inteligente**, capaz de administrar organizaciones de distintas industrias, conectar sus canales y automatizar progresivamente sus funciones operativas, administrativas y estratégicas, manteniendo seguridad, trazabilidad y supervisión humana.

## 13. Related pages

| Page | Path | Relationship |
|---|---|---|
| ☸️ DevOps & Platform Engineering | `documentation/pages/🤖 AI Architect Roadmap/☸️ DevOps & Platform Engineering 3a50bde8acd580c980d3c690e3860045.md` | DevOps, platform engineering and lifecycle workflows used by SBM Suite. |

## 14. Subpages

| Subpage | Path | Description | Status |
|---|---|---|---|

## 15. Document boundary

Esta página documenta la visión, arquitectura, componentes, estado, validación y roadmap de SBM Suite.

No sustituye los contextos operacionales de `SBM-SUITE/context/`, los contextos de cada proyecto, los contratos de API, los scripts ejecutables ni la evidencia QA original. No contiene secretos ni acredita como completado un objetivo que permanezca `active` o `pending`.
