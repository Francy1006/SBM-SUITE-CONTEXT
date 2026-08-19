# 🏢 SBM-Suite

> **Nota de arquitectura 2026-08-16:** `sbm-comercial` y `sbm-digital-api` se conservan solo como conceptos históricos del roadmap. No son proyectos aprobados para crear actualmente; el diseño vigente prioriza APIs de marca + stores/mobile/client channels directos.
>
> **Last updated:** 2026-08-19
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

- `DP-API`;
- `SBM-MANAGER`.

Antes de continuar con nuevos módulos de negocio, se implementará una base transversal de calidad y seguridad.

#### Separación entre `SBM-API` y `DP-API`

Actualmente `SBM-API` todavía contiene métodos y endpoints que corresponden a `DP-API`.

Se está ejecutando una migración para establecer responsabilidades definitivas.

##### Estado deseado

`SBM-API`:

- procesos internos;
- funciones críticas;
- administración SBM;
- lógica transversal;
- selección de marca o franquicia;
- operaciones no expuestas directamente al cliente.

`DP-API`:

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

1. Eliminar de `SBM-API` las funciones que correspondan a `DP-API`.
2. Eliminar duplicaciones.
3. Establecer contratos claros entre ambas APIs.
4. Separar correctamente permisos y usuarios.
5. Preparar comunicación síncrona y asíncrona.
6. Documentar responsabilidades por servicio.

#### Cierre validado de `SBM-MANAGER-002` — 2026-08-14

El frontend `SBM-MANAGER` completó la corrección de ownership canónico para los flujos cliente evidenciados de Service, Catalog y Provider:

- las operaciones cliente usan `dpApi` hacia `DP-API`;
- las consultas internas de franquicia permanecen en `sbmApi` hacia `SBM-API`;
- los contratos evidenciados de Catalog, Service y Provider quedaron alineados con `DP-API`;
- el cierre fue validado con 45 tests passing, 0 failures, coverage 70.14%, SonarScanner exit code 0 y server-side Quality Gate `PASSED`.

Este cierre corrige el consumo del frontend; no acredita eliminación de endpoints duplicados que todavía puedan existir en `SBM-API`.

### 7. Estado validado de Context y Documentation

| Objective ID | Project | Objective | Status | Validation |
|---|---|---|---|---|
| OBJ-CTX-013 | SBM-SUITE | Corregir y validar el workflow de documentación de `SBM-SUITE/context`, incluyendo `documentation-deploy.sh`, `documentation-upgrade.sh` y el flujo completo posterior a `context-upgrade`. | completed | `implementation-closure` y `context-upgrade` completados; Context/Documentation quedaron centralizados bajo `SBM-SUITE/context`, Documentation opera globalmente y QA fue validado estructuralmente como `not-applicable` al no existir `scripts/qa-check.sh`. |
| OBJ-CTX-001 | SBM-SUITE | Validate and stabilize the expanded context governance model, synchronized section patches and project-tree evidence | completed | Lifecycle-only/no-op closure registrada el 2026-08-13; `implementation-closure` y `context-upgrade` completados. QA fue `not-applicable` porque `scripts/qa-check.sh` no existe para `sbm-suite-context`; no se acreditan cambios de implementación. |
| SBM-MANAGER-002 | SBM-MANAGER | Corregir SBM-MANAGER para consumir correctamente SBM-API y DP-API según ownership canónico. | completed | Cierre registrado el 2026-08-14; Service, Catalog y Provider consumen `DP-API` mediante `dpApi`, las consultas internas de franquicia permanecen en `SBM-API` mediante `sbmApi`, y QA registró 45/45 tests, coverage 70.14% y Quality Gate `PASSED`. |
| OBJ-CTX-041 | SBM-SUITE | Permitir que `context-upgrade.sh` acepte exactamente un archivo `input/context-upgrade*.zip` y `documentation-upgrade.sh` exactamente un `documentation/input/documentation-upgrade*.zip`, incluyendo sufijos generados por el cliente como `(32)`, sin renombrado manual; mantener validación de manifest/workflow y rechazo de entradas ambiguas o no válidas. | completed | Cierre registrado el 2026-08-17; la implementación acepta exactamente un ZIP con prefijo de workflow, soporta sufijos del cliente sin renombrado manual, rechaza entradas ambiguas/no válidas y preserva la validación canónica de manifest/workflow. QA completo de Context y la cola transversal con SonarQube pasaron para los cinco repositorios registrados. |

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

#### `SBM-API`

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

`DP-API` es la primera API cliente de SBM Suite y corresponde a Ditaly Pasta.

Las futuras marcas podrán incorporar APIs propias cuando exista una necesidad funcional real.

---

### 5. Arquitectura general

```
                         SBM Suite

                   Usuarios internos
                          │
                          ▼
                    SBM-MANAGER
                          │
                          ▼
                       SBM-API
                API interna transversal
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
     DP-API       futuras APIs cliente   SBM-AI-ASSISTANT
 Primera API                              IA, RAG, Tools,
 cliente                                  Agentes y MCP
        │
        └──────────────┐
                       ▼
                    SBM-DB
             PostgreSQL / Flyway
       autoridad de esquemas y migraciones
```

Arquitectura futura ampliada:

```
Usuarios internos
       │
       ▼
SBM-MANAGER
       │
       ▼
SBM-API
       │
       ├── SBM-AI-ASSISTANT
       ├── sbm-digital-api
       ├── DP-API
       ├── futuras APIs cliente
       ├── SBM-DB
       ├── Kafka
       ├── Redis / Celery
       └── servicios externos

Usuarios públicos
       │
       ├── KS-STORE
       ├── sbm-comercial
       ├── futuras tiendas
       ├── aplicaciones móviles
       ├── marketplaces
       └── redes sociales
```

---

## 6. Components

### 7. Repositorios y aplicaciones

#### `SBM-MANAGER`

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

#### `SBM-API`

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

#### `DP-API`

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

#### `SBM-AI-ASSISTANT`

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

Conectar `SBM-AI-ASSISTANT` con:

1. `SBM-API`;
2. `DP-API`.

Flujo objetivo:

```
Usuario
   │
   ▼
Slack / Chat / Web
   │
   ▼
SBM-AI-ASSISTANT
   │
   ├── detecta intención
   ├── valida permisos
   ├── selecciona Tool o Agent
   ├── consulta SBM-API o DP-API
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

#### `SBM-DB`

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

Estos datos de marca se incorporarán cuando comience formalmente la etapa de publicación de `KS-STORE`.

##### Estado

🚧 En desarrollo.

#### `KS-STORE`

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

- `SBM-API`;
- `DP-API`;
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
- aislamiento de `SBM-API`.

##### Justificación

Esta API permite que `sbm-comercial`, `KS-STORE` y futuros canales consuman una capa especializada sin conectarse directamente a múltiples servicios internos.

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

### Evidencia actual de `SBM-MANAGER`

La evidencia de cierre de `SBM-MANAGER-002` del `2026-08-14` registra:

- 45 tests collected y 45 passed;
- 0 failures;
- coverage 70.14%;
- SonarScanner exit code 0;
- scanner execution `SUCCESS`;
- server-side Quality Gate `PASSED`;
- runtime Docker.

### Evidencia de cierre de `OBJ-CTX-041`

La evidencia de cierre registra:

- estado lifecycle `completed`;
- Context QA `passed`;
- cola transversal secuencial con SonarQube `passed`;
- DP-API, sbm-ai-assistant, SBM-API, SBM-DB y SBM-MANAGER `passed`;
- soporte validado para un único ZIP con prefijo `context-upgrade*` o `documentation-upgrade*`, incluyendo sufijos generados por el cliente sin renombrado manual.

## 11. Known limitations

Limitaciones y transiciones explícitas en el documento fuente:

- `SBM-API` todavía contiene métodos y endpoints que corresponden a `DP-API`;
- la separación definitiva entre `SBM-API` y `DP-API` continúa en evolución;
- PostgreSQL podrá mantenerse inicialmente fuera del clúster para evitar complejidad innecesaria;
- varios servicios, agentes, canales y componentes de infraestructura permanecen planificados.

## 12. Roadmap

### Objetivos actuales de `SBM-MANAGER`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| SBM-MANAGER-001 | Integrar SBM-MANAGER completamente a SBM Suite, incluyendo contextos, lifecycle scripts, QA/SonarQube, registro en SBM-AI-ASSISTANT, sincronización global y actualización del diagrama canónico de arquitectura en SUITE_CONTEXT.md. | active | 5 | 2026-08-07 | FEATURE-integrates-sbm-manager |
| SBM-MANAGER-003 | Corregir y completar QA de SBM-MANAGER. | pending | 5 | N/A | `BUGFIX-completes-manager-qa` |

`SBM-MANAGER-001` permanece **active** y `SBM-MANAGER-003` permanece **pending**. `SBM-MANAGER-002` fue retirado del roadmap tras su cierre validado y quedó registrado en `Current state`.

### Objetivo activo de `SBM-DB`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| SBM-DB-001 | habilitación de SBM-DB | active | 5 | 2026-08-07 | FEATURE-enables-sbm-db |

Este objetivo permanece **active**. Su presencia aquí no representa cierre ni implementación completada.

### Objetivos actuales de `SBM-SUITE/context`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| OBJ-DOC-001 | Implement the manual documentation deploy and upgrade workflow with dedicated RAG and Qdrant collection | pending | 5 | N/A | FEATURE-adds-documentation-workflow |
| OBJ-CTX-002 | Habilitar tooling transversal desde SBM-SUITE/context para crear, comparar, propagar y actualizar artefactos comunes sobre uno, varios o todos los repositorios físicos actuales. | active | 5 | N/A | FEATURE-automates-cross-project-flows |
| OBJ-CTX-003 | Separar QA y Context mediante una estructura específica por proyecto. | pending | 5 | N/A | FEATURE-separates-qa-context |
| OBJ-CTX-004 | Crear SBM-CORE para scheduler/cron, PostgreSQL de flags/estado, Celery, Redis, retries/idempotency y Kafka solo donde el patrón event-driven lo justifique; sin lógica financiera ni de seguridad de dominio. | pending | 5 | N/A | FEATURE-enables-sbm-core |
| OBJ-CTX-005 | Crear SBM-UTIL como servicio reutilizable Java/Spring Boot para email, archivos, APIs externas, conectores determinísticos, transformaciones técnicas y tipos de cambio oficiales consumidos por servicios/agentes. | pending | 5 | N/A | FEATURE-enables-sbm-util |
| OBJ-CTX-006 | Habilitar Scrum Agent para convertir Objectives en Jira Epic/Issue, priorizar backlog y coordinar dependencias, procesos asíncronos y activaciones IA mediante SBM-CORE/Control API. | pending | 5 | N/A | FEATURE-enables-scrum-agent |
| OBJ-CTX-007 | Habilitar Igor Agent como responsable técnico de QA automation, DevOps/SRE, infraestructura y troubleshooting, integrándolo a CI/CD y a los gates técnicos sin mezclar QA con Security. | pending | 5 | N/A | FEATURE-enables-igor-agent |
| OBJ-CTX-008 | Habilitar el Security Gate posterior a QA y previo a release: ejecución automatizada, evidencias, findings, mitigación/prevención, aprobación humana en SBM-SECURITY y retorno obligatorio a Development cuando Security rechace. | pending | 5 | N/A | FEATURE-enables-security-flow |
| OBJ-CTX-009 | Evolucionar la capacidad security-agent hacia la célula nombrada en SBM-AI-ASSISTANT liderada por Batman Agent e integrada por Alfred, Robin, Gotham, Joker, Queen, Darth Maul, Cerberus y Hercules, usando SBM-SECURITY-API y herramientas locales/dockerizadas/externas bajo autorización. | pending | 5 | N/A | FEATURE-enables-security-agents |
| OBJ-CTX-010 | Crear SBM-AI-MANAGER como frontend/control plane para registrar, visualizar, configurar y operar agentes; tecnología .NET/Blazor queda como candidata a validar al activar. | pending | 5 | N/A | FEATURE-enables-ai-manager |
| OBJ-CTX-011 | Completar INIT_CONTEXT.md para soportar creación/onboarding de nuevos proyectos SBM. | pending | 5 | N/A | FEATURE-completes-project-onboarding |
| OBJ-CTX-012 | Mantener INIT_CONTEXT.md como contrato operativo y crear SBM_AGENT.md como bootstrap mínimo para chats nuevos sin duplicar reglas. | active | 5 | N/A | FEATURE-separates-agent-init-flow |
| OBJ-CTX-015 | Crear KS-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para venta/importación KS: Product/Material/Service/Catalog/Ticket, inventario, costos de importación, pricing multimoneda y trazabilidad; arriendo queda fuera del alcance inmediato. | pending | 5 | N/A | FEATURE-enables-ks-api |
| OBJ-CTX-016 | Crear PC-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para operativos y derivaciones: agendamiento, Client/Customer, QR, confirmación, comisión, conciliación y suscripción mensual. | pending | 5 | N/A | FEATURE-enables-pc-api |
| OBJ-CTX-017 | Crear CG-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para trámites, documentos, etapas, dependencias, calendarización, proveedores y planos. | pending | 5 | N/A | FEATURE-enables-cg-api |
| OBJ-CTX-018 | Crear SBM-CALCULATION en Python/FastAPI con pandas, scikit-learn y statsmodels para fórmulas, precios, FX, impuestos, comisiones, provisiones, costos, conciliaciones, regresiones y capacidades ML autorizadas. | pending | 5 | N/A | FEATURE-enables-sbm-calculation |
| OBJ-CTX-019 | Crear SBM-SECURITY como frontend humano de Security: findings, scans, vulnerabilidades, evidencias, riesgos, protocolos, planes de mitigación/prevención, reportes y aprobación/rechazo del Security Gate consumiendo SBM-SECURITY-API. | pending | 5 | N/A | FEATURE-enables-sbm-security |
| OBJ-CTX-020 | Crear SBM-MARKETING como API Node.js/TypeScript/NestJS para datos de redes, SEO, campañas, métricas, calendarizaciones, sesiones foto/video, pago de promociones, arriendo de equipos, contratación de servicios e integraciones sociales. | pending | 5 | N/A | FEATURE-enables-sbm-marketing |
| OBJ-CTX-021 | Crear SBM-CONTENT en Python/FastAPI para assets y workflows de producción, generación y edición de contenido, integrando DaVinci/Medici y herramientas creativas autorizadas como Photoshop y Blender. | pending | 5 | N/A | FEATURE-enables-sbm-content |
| OBJ-CTX-022 | Crear SBM-CONTROL como control plane global de SBM Suite: health/status, logs, métricas/reportes, cron/schedulers, workers/colas, Context/Objectives/Documentation, QA, Security, deploys, alertas y backups. | pending | 5 | N/A | FEATURE-enables-sbm-control |
| OBJ-CTX-023 | Crear SBM-MOBILE en React Native para SBM User y operaciones administrativas aprobadas. | pending | 5 | N/A | FEATURE-enables-sbm-mobile |
| OBJ-CTX-024 | Crear KS-STORE clonando/adaptando __BASE-STORE como vitrina/commerce pública de Tickets KS bajo dominio propio. | pending | 5 | N/A | FEATURE-enables-ks-store |
| OBJ-CTX-025 | Crear PC-STORE clonando/adaptando __BASE-STORE como canal público de servicios/Tickets PC bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-pc-store |
| OBJ-CTX-026 | Crear CG-STORE clonando/adaptando __BASE-STORE como canal público de servicios/Tickets CG bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-cg-store |
| OBJ-CTX-027 | Crear KS-MOBILE clonando/adaptando __BASE-MOBILE en React Native para KS/Franchise User. | pending | 5 | N/A | FEATURE-enables-ks-mobile |
| OBJ-CTX-028 | Crear PC-MOBILE clonando/adaptando __BASE-MOBILE en React Native para PC/Franchise User. | pending | 5 | N/A | FEATURE-enables-pc-mobile |
| OBJ-CTX-029 | Crear CG-MOBILE clonando/adaptando __BASE-MOBILE en React Native para CG/Franchise User. | pending | 5 | N/A | FEATURE-enables-cg-mobile |
| OBJ-CTX-030 | Crear KS-CLIENT clonando/adaptando __BASE-CLIENT para Client User KS, inicialmente control de inventario/equipos y capacidades autorizadas de monitoreo/operación. | pending | 5 | N/A | FEATURE-enables-ks-client |
| OBJ-CTX-031 | Crear PC-CLIENT clonando/adaptando __BASE-CLIENT para Client User PC, incluyendo operativos/derivaciones, agenda, QR/confirmaciones y conciliación operativa. | pending | 5 | N/A | FEATURE-enables-pc-client |
| OBJ-CTX-032 | Crear PC-CUSTOMER clonando/adaptando __BASE-CUSTOMER para PC Customer: ficha, QR, agendamiento, confirmación y seguimiento del servicio con tratamiento reforzado de datos personales/salud. | pending | 5 | N/A | FEATURE-enables-pc-customer |
| OBJ-CTX-033 | Crear CG-CLIENT clonando/adaptando __BASE-CLIENT para seguimiento de etapas de tramitación, dependencias, documentos faltantes, información general y FAQ. | pending | 5 | N/A | FEATURE-enables-cg-client |
| OBJ-CTX-034 | Expandir SBM-AI-ASSISTANT con el catálogo canónico de agentes nombrados, jerarquías/gobierno, permisos, herramientas y activación bajo demanda; Scrum Agent/SBM Agent coordinan y por defecto se prefieren APIs, jobs y servicios determinísticos antes de ejecutar IA. | pending | 5 | N/A | FEATURE-expands-named-agents |
| OBJ-CTX-035 | Habilitar almacenamiento de objetos/documentos transversal para archivos, planos, assets, evidencias y contenido, con aislamiento, versionado y políticas de acceso. | pending | 5 | N/A | FEATURE-enables-object-storage |
| OBJ-CTX-036 | Definir despliegue productivo compartido para KS/PC/CG con gateway/reverse proxy, TLS, backups y separación de servicios públicos/internos; SonarQube permanece QA temporal y SBM-SECURITY-API/SECURITY tooling se aísla del runtime de negocio. | pending | 5 | N/A | FEATURE-defines-prod-topology |
| OBJ-CTX-037 | Corregir objective-git-finalize.sh para preflight multi-repo, commit/push de branch FEATURE/BUGFIX, ejecutar git push --set-upstream origin <branch> cuando la primera publicación no tenga upstream, merge --no-ff a main, push de main y normalización segura; sin force-push ni borrado de ramas. | pending | 5 | N/A | BUGFIX-fixes-git-finalizer |
| OBJ-CTX-038 | Estandarizar el lifecycle/Git Flow transversal main-only, batch 1..N multiproyecto, QA completo y Documentation obligatorios, finalización directa y cleanup de branch temporal. | active | 5 | N/A | FEATURE-standardizes-suite-governance |
| OBJ-CTX-039 | Habilitar el framework de proyectos base __BASE-*: __BASE-FRANCHISE-API, __BASE-STORE, __BASE-MOBILE, __BASE-CLIENT, __BASE-CUSTOMER; creación por clone/adaptación, versionado de origen, tracking de derivados, propagación controlada de cambios, resolución de divergencias y validación por agentes. | pending | 5 | N/A | FEATURE-enables-base-project-inheritance |
| OBJ-CTX-040 | Crear SBM-SECURITY-API en Go/Gin/PostgreSQL como backend aislado de Security para pentests/scans, tool runs, findings, evidencias, políticas, riesgos y approvals; integra herramientas locales/dockerizadas/externas y usa SBM-CORE solo para scheduling/jobs, sin lógica Security en Core. | pending | 5 | N/A | FEATURE-enables-security-api |

Los objetivos anteriores reflejan literalmente el estado operativo actual de Context; `pending` no acredita implementación.

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

La sincronización programada de Confluence en `SBM-AI-ASSISTANT` deberá migrarse desde APScheduler hacia Celery Beat cuando se implemente la infraestructura distribuida.

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
SBM-AI-ASSISTANT
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

Actualmente `SBM-AI-ASSISTANT` incluye:

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

Será la primera integración operativa de `SBM-AI-ASSISTANT`.

Responsabilidades:

- detectar la intención del usuario;
- determinar si corresponde consultar `SBM-API` o `DP-API`;
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
SBM-AI-ASSISTANT
   │
   ▼
SBM API Integration Agent
   │
   ├── SBM-API
   └── DP-API
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
SBM-AI-ASSISTANT
   │
   ├── SBM API Integration Agent
   │      ├── SBM-API
   │      └── DP-API
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

La evolución de `SBM-AI-ASSISTANT` incluirá:

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

1. Finalizar la separación entre `SBM-API` y `DP-API`.
2. Eliminar endpoints y procesos duplicados.
3. Estabilizar `product` y `material`.
4. Implementar QA transversal.
5. Incorporar pruebas unitarias y de integración.
6. Integrar cobertura y SonarQube.
7. Incorporar herramientas de seguridad gratuitas o locales.
8. Documentar cada repositorio.
9. Migrar progresivamente la gestión a Azure DevOps.
10. Conectar `SBM-AI-ASSISTANT` con `SBM-API` y `DP-API`.
11. Implementar Redis y Celery.
12. Migrar el scheduler de IA a Celery Beat.
13. Incorporar Kafka.
14. Implementar Kubernetes.
15. Incorporar observabilidad.

---

### 18. Desarrollo posterior

1. `KS-STORE`.
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
- aplicar posteriormente lo aprendido en `SBM-AI-ASSISTANT` y SBM Suite.

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


### Additional lifecycle records synchronized from Context — 2026-08-19

| Objective ID | Project | Objective | Status | Priority | Target date | Branch |
|---|---|---|---|---:|---|---|
| SBM-MANAGER-004 | SBM-MANAGER | Extender la UI genérica para Equipment, Package obligatorio, composición/dosificación de Catalog y Price multimoneda sin duplicar lógica backend. | pending | 5 | N/A | FEATURE-expands-item-management |
| SBM-MANAGER-005 | SBM-MANAGER | Habilitar módulo de documentos y planos para CG con editor drag-and-drop, versionado/exportación e integración OCR/IA mediante servicios autorizados. | pending | 5 | N/A | FEATURE-enables-plan-editor |
| SBM-MANAGER-006 | SBM-MANAGER | Definir navegación y autorización multi-brand/multi-role para SBM User y Brand User, consumiendo SBM-API y Franchise APIs mediante contratos estables sin acoplar la UI a DP-API. | pending | 5 | N/A | FEATURE-enables-multibrand-navigation |
| SBM-API-001 | SBM-API | Consolidar identidad/autorización multinivel para SBM User, Franchise/Brand User, Client User y Customer User cuando aplique, preservando franchise como alcance canónico de marca y roles/permisos/restricciones backend. | pending | 5 | N/A | FEATURE-expands-identity-model |
| SBM-API-002 | SBM-API | Renombrar el runtime/container legacy `sbm-core` usado actualmente por SBM-API para liberar el nombre del futuro proyecto `SBM-CORE` y evitar colisión de servicio/red. | pending | 5 | N/A | BUGFIX-renames-sbm-api-runtime |
| SBM-API-003 | SBM-API | Formalizar el contrato transversal SBM-API ↔ Franchise APIs para autenticación/autorización, franchise/brand scope, propagación de identidad, errores y límites de ownership, evitando dependencias específicas de DP. | pending | 5 | N/A | FEATURE-defines-franchise-api-contract |
| SBM-DB-003 | SBM-DB | Definir e implementar la topología de datos multimarcas para SBM, DP histórico, KS, PC y CG con aislamiento lógico/credenciales, preservando SBM-DB como autoridad Flyway y no como gateway de consultas. | pending | 5 | N/A | FEATURE-defines-multibrand-data |
| SBM-DB-004 | SBM-DB | Agregar Equipment como dominio y formalizar Package obligatorio para Product, Material, Service, Equipment, Catalog y Ticket; Service usa un Package lógico no físico. | pending | 5 | N/A | FEATURE-adds-equipment-package |
| SBM-DB-005 | SBM-DB | Modelar Catalog como composición/BOM configurable con componentes Product, Material, Service y Equipment, cantidades/dosificación/unidades, manteniendo Ticket como unidad vendida/reportada. | pending | 5 | N/A | FEATURE-adds-catalog-components |
| SBM-DB-006 | SBM-DB | Extender Price para base_net_amount, net_amount, gross, IVA, impuestos adicionales, moneda y tipo de cambio versionado, incluyendo USD observado y futuras monedas/UF. | pending | 5 | N/A | FEATURE-adds-multicurrency-pricing |
| SBM-DB-007 | SBM-DB | Modelar trazabilidad de adquisición y movimiento: orden de compra, factura, IVA crédito, guía de despacho, traslado interno, venta a cliente/franquiciado, provisión y costo real. | pending | 5 | N/A | FEATURE-adds-procurement-trace |
| SBM-DB-008 | SBM-DB | Modelar costos de importación KS por compra/unidad: FOB, naviera, embarcador, aduana, desconsolidación, seguros, fletes, bodega, grúas, garantía, reposición y otros servicios instanciados por adquisición. | pending | 5 | N/A | FEATURE-adds-ks-import-costs |
| SBM-DB-009 | SBM-DB | Modelar PC para operativos y derivaciones: Client/Customer, agendamiento, QR, estados, comisión configurable, conciliación y suscripción mensual por máximo entre valor fijo y pacientes tratados. | pending | 5 | N/A | FEATURE-adds-pc-service-model |
| SBM-DB-010 | SBM-DB | Modelar CG para trámites, documentos, planos, etapas, dependencias, calendarización y proveedores externos, manteniendo datos/documentos sensibles con clasificación explícita. | pending | 5 | N/A | FEATURE-adds-cg-workflow-model |
| SBM-DB-011 | SBM-DB | Definir contratos/migraciones compatibles con __BASE-FRANCHISE-API y sus derivados, separando estructuras comunes de extensiones/configuración por franchise y evitando dependencias de datos específicas de DP en la base reusable. | pending | 5 | N/A | FEATURE-defines-base-data-contract |
| DP-ARCH-001 | DP-API | Estabilizar satisfactoriamente DP-API trabajando con SBM-API como implementación funcional de referencia, preservando datos/comportamiento Ditaly y cerrando contratos de integración antes de extraer cualquier base reusable. | pending | 5 | N/A | FEATURE-stabilizes-dp-sbm-integration |
| BASE-FRANCHISE-001 | __BASE-FRANCHISE-API | Después de completar DP-ARCH-001, generar __BASE-FRANCHISE-API desde la implementación validada de DP-API, remover/configurar comportamiento específico DP, estandarizar módulos opcionales y registrar DP-API como primer derivado controlado del BASE. | pending | 5 | N/A | FEATURE-creates-franchise-base-from-dp |
| OBJ-CTX-042 | SBM-SUITE | Integrar Documentation Markdown con Notion mediante sincronización Git→Notion controlada, preservando Git/Markdown como source of truth, estructura de páginas, IDs estables, trazabilidad y detección de cambios; bidireccionalidad queda fuera del alcance inicial. | pending | 5 | N/A | FEATURE-syncs-documentation-to-notion |
| OBJ-CTX-043 | SBM-SUITE | Integrar Objectives con Jira como backlog organizado por Proyecto→Epic→Issue/Task, manteniendo mapping Objective ID↔Jira ID, estado, prioridad y dependencias sin duplicados; inicialmente operado por SBM Agent/SBM-UTIL y futuramente administrado por Scrum Agent. | pending | 5 | N/A | FEATURE-syncs-objectives-to-jira |
| OBJ-CTX-044 | SBM-SUITE | Estandarizar contratos Agent↔API/Tool en SBM-AI-ASSISTANT para request/response, scopes/permisos, approvals, auditoría, idempotencia, errores y evidencias, evitando integraciones ad hoc específicas por agente. | pending | 5 | N/A | FEATURE-standardizes-agent-tool-contracts |
| OBJ-CTX-045 | SBM-SUITE | Implementar Xavier Agent como coordinador de conversaciones humanas y reuniones multiagente, gestionando sesiones, participantes, turnos, contexto conversacional, incorporación y retiro dinámico de agentes, permisos y auditoría. | pending | 5 | N/A | FEATURE-adds-suite-objectives |
| OBJ-CTX-046 | SBM-SUITE | Diseñar e implementar SBM Voice Interface incluyendo STT/TTS, Voice Registry, identidad de voz por agente, wake word, dispositivo físico, integración textual con SBM-MANAGER, autenticación humana/dispositivo, autorización por sesión, anti-spoofing/replay y auditoría. | pending | 5 | N/A | FEATURE-adds-suite-objectives |
| OBJ-CTX-047 | SBM-SUITE | Diseñar arquitectura Local/Cloud AI Runtime con ejecución local opcional de agentes, RAG, embeddings, Vector DB, context cache y fallback seguro hacia proveedores cloud. | pending | 5 | N/A | FEATURE-adds-suite-objectives |
| OBJ-CTX-048 | SBM-SUITE | Corregir la integración de Confluence de SBM-AI-ASSISTANT, restaurando y validando credenciales/configuración requeridas para ingestión y sincronización sin modificar innecesariamente la implementación existente. | pending | 5 | N/A | FEATURE-adds-suite-objectives |

These rows mirror current Context lifecycle state only; `pending` does not imply implementation and no terminal state is inferred. `OBJ-CTX-045` through `OBJ-CTX-048` were synchronized as planning-only records on 2026-08-19; no voice, local-AI or Confluence implementation is claimed by their registration.


### Multi-brand SBM baseline — 2026-08-16

- DP/Ditaly Pasta: closed, one year of real data, historical/reference implementation.
- Production targets: Kiseki Tech (KS), PortalConvenios.cl (PC), Consorcio y Gestión (CG).
- Canonical application/project display names are uppercase; literal filesystem paths remain unchanged until explicit migration.
- Shared projects include `SBM-CORE`, `SBM-CALCULATION`, `SBM-UTIL`, `SBM-AI-MANAGER`, `SBM-SECURITY`, `SBM-SECURITY-API`, `SBM-MARKETING`, `SBM-CONTENT`, `SBM-CONTROL`, `SBM-MOBILE`.
- `SBM-CALCULATION`: Python/FastAPI + regression/ML stack.
- `SBM-MARKETING`: Node.js/TypeScript/NestJS API.
- `SBM-CONTENT`: Python/FastAPI.
- `SBM-SECURITY-API`: Go/Gin/PostgreSQL. `SBM-SECURITY` is the human review front; named Security agents run in `SBM-AI-ASSISTANT`; `SBM-CORE` schedules jobs only.

```text
__BASE-FRANCHISE-API → DP-API / KS-API / PC-API / CG-API
__BASE-STORE         → KS-STORE / PC-STORE / CG-STORE
__BASE-MOBILE        → KS-MOBILE / PC-MOBILE / CG-MOBILE
__BASE-CLIENT        → KS-CLIENT / PC-CLIENT / CG-CLIENT
__BASE-CUSTOMER      → PC-CUSTOMER
```

`OBJ-CTX-038` remains **active** and the current temporary branch contains first-publication upstream handling, the main-only transversal Git policy, minimal `SBM_AGENT.md` bootstrap and allowlisted common-artifact propagation. `OBJ-CTX-041` is **completed** on `FEATURE-standardizes-suite-governance`; its validated workflow-prefixed upgrade ZIP handling is recorded in `Current state`. `OBJ-CTX-039` and `OBJ-CTX-040` remain **pending** and describe planned base/derived inheritance and the isolated Security API respectively. `OBJ-CTX-034` remains planning for the named-agent catalog and on-demand activation.

### Legacy digital roadmap concepts

`sbm-comercial` and `sbm-digital-api` remain historical roadmap concepts, not current approved project-creation objectives. The current target favors direct brand APIs plus brand stores/client/mobile channels. Reactivate a transversal commercial portal/BFF only if a concrete cross-brand requirement justifies it.

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
