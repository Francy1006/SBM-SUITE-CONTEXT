# 🧪QA & Testing

> Estrategia transversal de calidad para SBM Suite.
> 
> 
> Esta página define cómo se validarán aplicaciones, APIs, bases de datos, integraciones, agentes IA, infraestructura y procesos de despliegue.
> 
> La calidad no se considera una etapa final. Debe estar integrada desde el diseño, desarrollo, pull request, CI/CD, despliegue y operación.
> 

---

# 1. Objetivo

Crear un estándar de QA aplicable a todos los proyectos de SBM Suite para:

- reducir errores;
- evitar regresiones;
- validar integraciones;
- mejorar mantenibilidad;
- aumentar seguridad;
- asegurar contratos entre servicios;
- medir cobertura;
- validar rendimiento;
- automatizar controles;
- producir evidencia verificable para el portafolio.

---

# 2. Alcance

El estándar QA debe cubrir:

- `sbm-manager`;
- `sbm-api`;
- `dp-api`;
- `sbm-ai-assistant`;
- `sbm-db`;
- `sbm-comercial`;
- `sbm-digital-api`;
- `ks-store`;
- integraciones externas;
- Redis y Celery;
- Kafka;
- Kubernetes;
- flujos n8n;
- agentes IA;
- RAG;
- modelos ML;
- pipelines CI/CD.

---

# 3. Principios

1. **Shift-left testing**
    
    Las pruebas comienzan durante el desarrollo.
    
2. **Automation-first**
    
    Todo control repetible debe automatizarse.
    
3. **Risk-based testing**
    
    Se priorizan los procesos con mayor impacto.
    
4. **Test pyramid**
    
    Se mantienen muchas pruebas unitarias, suficientes pruebas de integración y menos pruebas E2E.
    
5. **Fast feedback**
    
    Los errores deben detectarse lo antes posible.
    
6. **Deterministic tests**
    
    Las pruebas deben producir resultados consistentes.
    
7. **Independent environments**
    
    Las pruebas no deben depender de datos manuales o servicios productivos.
    
8. **Quality gates**
    
    El código no debe avanzar si no supera controles mínimos.
    
9. **Contract stability**
    
    Los servicios deben respetar contratos definidos.
    
10. **Portfolio evidence**
    
    Los resultados deben ser visibles mediante reportes, dashboards y documentación.
    

---

# 4. Pirámide de pruebas

```
              E2E
           ─────────
        Integration Tests
      ───────────────────
        Component Tests
    ───────────────────────
          Unit Tests
──────────────────────────────
```

## Distribución recomendada

| Nivel | Propósito | Cantidad esperada |
| --- | --- | --- |
| Unit | Validar lógica aislada | Alta |
| Component | Validar módulos completos | Media-alta |
| Integration | Validar servicios y dependencias | Media |
| Contract | Validar comunicación entre APIs | Media |
| E2E | Validar flujos críticos completos | Baja |
| Performance | Validar capacidad y estabilidad | Según riesgo |
| Security | Validar exposición y vulnerabilidades | Continua |

---

# 5. Tipos de pruebas

| Tipo | Objetivo |
| --- | --- |
| Unit Testing | Validar funciones, clases y reglas aisladas |
| Integration Testing | Validar interacción entre componentes |
| API Testing | Validar endpoints, schemas y errores |
| Contract Testing | Validar compatibilidad entre servicios |
| Component Testing | Validar módulos completos |
| End-to-End Testing | Validar flujos reales |
| Regression Testing | Evitar que cambios rompan funcionalidades existentes |
| Smoke Testing | Validar disponibilidad básica |
| Sanity Testing | Validar cambios específicos |
| Performance Testing | Medir carga, estrés y estabilidad |
| Security Testing | Detectar vulnerabilidades |
| Accessibility Testing | Validar acceso inclusivo |
| Database Testing | Validar migraciones, constraints y queries |
| AI Evaluation | Validar respuestas, retrieval y tools |
| Chaos and Resilience Testing | Validar comportamiento ante fallas |

---

# 6. Estrategia por proyecto

## `sbm-api`

Debe incluir:

- pruebas unitarias de servicios y reglas;
- pruebas de serializers;
- pruebas de permisos;
- pruebas de autenticación;
- pruebas de endpoints;
- pruebas de transacciones;
- pruebas de integración con PostgreSQL;
- pruebas de contratos;
- pruebas de errores;
- pruebas de concurrencia;
- pruebas de integración con servicios externos.

## `dp-api`

Debe incluir:

- pruebas CRUD;
- pruebas de catálogo;
- pruebas de productos;
- pruebas de materiales;
- pruebas de precios;
- pruebas de proveedores;
- pruebas de sucursales;
- pruebas de permisos por cliente y marca;
- pruebas de integración con `sbm-api`;
- pruebas de contratos OpenAPI;
- pruebas de regresión.

## `sbm-manager`

Debe incluir:

- pruebas de componentes Vue;
- pruebas de composables;
- pruebas de stores Pinia;
- pruebas de navegación;
- pruebas de formularios;
- pruebas de estados de carga;
- pruebas de errores;
- pruebas de integración con APIs;
- pruebas E2E de procesos críticos.

## `sbm-comercial`

Debe incluir:

- pruebas de componentes React;
- pruebas de formularios;
- pruebas de routing;
- pruebas de estados;
- pruebas de integración;
- pruebas E2E;
- pruebas de accesibilidad;
- pruebas de SEO técnico cuando corresponda.

## `sbm-ai-assistant`

Debe incluir:

- pruebas unitarias de routers;
- pruebas de tools;
- pruebas de clientes API;
- pruebas de intención;
- pruebas de permisos;
- pruebas RAG;
- pruebas de recuperación;
- pruebas de prompts;
- pruebas de fallback;
- pruebas de integración con Slack;
- pruebas de agentes;
- pruebas de seguridad LLM;
- pruebas de evaluación automática.

## `sbm-db`

Debe incluir:

- pruebas de migraciones;
- pruebas de rollback cuando sea posible;
- pruebas de constraints;
- pruebas de índices;
- pruebas de integridad referencial;
- pruebas de seeds;
- pruebas de compatibilidad entre versiones;
- validación de tiempos de migración.

## `sbm-digital-api`

Debe incluir:

- pruebas unitarias;
- pruebas de controladores;
- pruebas de servicios;
- pruebas de guards;
- pruebas de caché;
- pruebas de rate limiting;
- pruebas WebSocket o SSE;
- pruebas de agregación de APIs;
- pruebas de contratos;
- pruebas de carga.

---

# 7. Backend Testing — Python y Django

## Herramientas

| Tool | Uso |
| --- | --- |
| pytest | Framework principal |
| pytest-django | Integración con Django |
| pytest-asyncio | Pruebas async |
| pytest-cov | Cobertura |
| Factory Boy | Fixtures y factories |
| Faker | Datos sintéticos |
| unittest.mock | Mocks |
| responses | Mock HTTP |
| respx | Mock HTTPX |
| freezegun | Control de fecha y hora |
| Testcontainers | Dependencias reales en contenedores |

## Estructura recomendada

```
tests/
├── unit/
├── integration/
├── api/
├── contracts/
├── factories/
├── fixtures/
└── conftest.py
```

## Reglas

- no depender de datos manuales;
- usar factories;
- aislar side effects;
- limpiar estado;
- controlar fecha y hora;
- evitar mocks excesivos en integración;
- probar casos exitosos y fallidos;
- probar permisos explícitamente.

---

# 8. FastAPI Testing

## Herramientas

- pytest;
- pytest-asyncio;
- HTTPX;
- FastAPI TestClient;
- respx;
- dependency overrides;
- Testcontainers.

## Casos

- health checks;
- validación Pydantic;
- errores 4xx y 5xx;
- autenticación;
- autorización;
- timeouts;
- tools;
- retries;
- integración con Qdrant;
- integración con LLM;
- integración con Slack;
- integración con APIs internas.

---

# 9. Node.js y NestJS Testing

## Herramientas

| Tool | Uso |
| --- | --- |
| Jest | Unit testing |
| Supertest | API testing |
| TestingModule | Pruebas NestJS |
| Testcontainers | Infraestructura real |
| MSW | Mock de APIs |
| Pact | Contract testing |

## Casos

- controllers;
- services;
- guards;
- interceptors;
- pipes;
- DTO validation;
- authentication;
- authorization;
- API aggregation;
- caching;
- rate limiting;
- WebSockets;
- SSE.

---

# 10. Vue Testing

## Herramientas

- Vitest;
- Vue Test Utils;
- Pinia Testing;
- Mock Service Worker;
- Playwright;
- Testing Library cuando aporte valor.

## Casos

- componentes;
- props;
- emits;
- slots;
- composables;
- stores;
- validación;
- formularios;
- rutas;
- loading;
- errores;
- permisos;
- interacción con APIs.

---

# 11. React Testing

## Herramientas

- Vitest;
- React Testing Library;
- Mock Service Worker;
- Playwright;
- jest-dom.

## Casos

- componentes;
- hooks;
- formularios;
- routing;
- estado;
- integración con APIs;
- errores;
- loading;
- accesibilidad;
- flujos comerciales.

---

# 12. API Testing

## Herramientas

| Tool | Uso |
| --- | --- |
| Bruno | Colecciones versionadas |
| Postman Free | Exploración manual |
| Newman | Automatización |
| OpenAPI | Contrato |
| Schemathesis | Property-based API testing |
| Pact | Contract testing |
| k6 | Performance API |

## Casos obligatorios

- códigos HTTP;
- schemas;
- headers;
- autenticación;
- permisos;
- filtros;
- paginación;
- ordenamiento;
- validación;
- errores;
- idempotencia;
- rate limiting;
- timeouts;
- versionado;
- compatibilidad.

---

# 13. Contract Testing

## Objetivo

Evitar que cambios en un servicio rompan consumidores.

## Relaciones prioritarias

```
sbm-manager → sbm-api
sbm-manager → dp-api
sbm-ai-assistant → sbm-api
sbm-ai-assistant → dp-api
sbm-digital-api → sbm-api
sbm-digital-api → APIs cliente
ks-store → dp-api
```

## Herramientas

- OpenAPI validation;
- Pact;
- Schemathesis;
- JSON Schema;
- AsyncAPI para eventos.

## Reglas

- contratos versionados;
- cambios incompatibles explícitos;
- pruebas en CI;
- consumidores identificados;
- deprecación documentada.

---

# 14. Database Testing

## Alcance

- migraciones;
- constraints;
- índices;
- triggers;
- funciones;
- vistas;
- seeds;
- performance;
- integridad.

## Herramientas

- PostgreSQL real;
- Testcontainers;
- Flyway;
- SQL scripts;
- pgTAP como opción futura;
- EXPLAIN ANALYZE.

## Pruebas mínimas

1. migración desde base vacía;
2. migración desde versión anterior;
3. validación de constraints;
4. validación de foreign keys;
5. validación de datos iniciales;
6. validación de índices;
7. validación de queries críticas;
8. validación de incompatibilidades.

---

# 15. End-to-End Testing

## Herramienta principal

Playwright.

## Flujos críticos iniciales

### Productos

```
Login
  ↓
Abrir módulo productos
  ↓
Crear producto
  ↓
Validar respuesta API
  ↓
Validar persistencia
  ↓
Editar producto
  ↓
Consultar producto
```

### Materiales

```
Login
  ↓
Crear material
  ↓
Asignar configuración
  ↓
Validar listado
  ↓
Editar
  ↓
Eliminar o desactivar
```

### AI Assistant

```
Enviar consulta
  ↓
Detectar intención
  ↓
Seleccionar tool
  ↓
Consultar API
  ↓
Validar permisos
  ↓
Responder
  ↓
Registrar traza
```

## Reglas

- limitar E2E a flujos críticos;
- evitar duplicar pruebas unitarias;
- ejecutar smoke E2E en CI;
- ejecutar suite completa en pipeline nocturno o release.

---

# 16. Performance Testing

## Herramientas

- k6;
- Locust;
- Prometheus;
- Grafana.

## Tipos

| Tipo | Objetivo |
| --- | --- |
| Load | Validar carga esperada |
| Stress | Encontrar límite |
| Spike | Validar aumentos repentinos |
| Soak | Validar estabilidad prolongada |
| Scalability | Medir crecimiento |
| Endurance | Detectar fugas o degradación |

## Métricas

- requests por segundo;
- latencia p50;
- latencia p95;
- latencia p99;
- tasa de error;
- uso CPU;
- memoria;
- conexiones;
- throughput;
- tiempo de respuesta DB;
- timeouts.

---

# 17. Security Testing

La seguridad detallada se mantiene en la página **Security & DevSecOps**, pero QA debe validar:

- autenticación;
- autorización;
- permisos por marca;
- inyección;
- exposición de datos;
- rate limiting;
- CORS;
- CSRF;
- secretos;
- dependencias;
- headers;
- APIs;
- contenedores;
- LLMs;
- tools.

## Herramientas

- OWASP ZAP;
- Burp Suite Community;
- Semgrep;
- Bandit;
- Trivy;
- Gitleaks;
- pip-audit;
- npm audit;
- Garak;
- Promptfoo.

---

# 18. Accessibility Testing

## Herramientas

- Playwright;
- axe-core;
- Lighthouse;
- browser accessibility tools.

## Casos

- navegación por teclado;
- contraste;
- labels;
- roles;
- foco;
- formularios;
- errores;
- lectores de pantalla;
- estructura semántica.

---

# 19. Visual Regression Testing

## Objetivo

Detectar cambios visuales inesperados.

## Herramientas

- Playwright screenshots;
- Storybook;
- Chromatic como alternativa opcional;
- Percy como alternativa opcional.

## Casos

- componentes críticos;
- dashboards;
- formularios;
- tiendas;
- vistas responsive;
- estados de error;
- estados de carga.

---

# 20. AI and RAG Testing

## Dimensiones

- exactitud;
- relevancia;
- groundedness;
- contexto recuperado;
- cobertura documental;
- seguridad;
- consistencia;
- latencia;
- costo;
- selección de tools.

## Herramientas

- Ragas;
- DeepEval;
- Promptfoo;
- Langfuse;
- datasets de evaluación;
- human review.

## Casos

- pregunta con respuesta;
- pregunta sin respuesta;
- documento desactualizado;
- acceso no autorizado;
- prompt injection;
- tool incorrecta;
- API caída;
- timeout;
- fallback;
- hallucination;
- cross-brand data leakage.

---

# 21. Agent Testing

Cada agente debe probar:

- intención;
- selección de tool;
- permisos;
- scope de marca;
- confirmación humana;
- inputs inválidos;
- outputs inválidos;
- timeout;
- retry;
- auditoría;
- fallback;
- operación parcial;
- errores externos.

## Niveles

1. unit tests del agente;
2. tool tests;
3. integration tests;
4. scenario tests;
5. end-to-end tests;
6. red teaming;
7. regression evaluation.

---

# 22. Test Data Management

## Estrategias

- factories;
- fixtures;
- datasets sintéticos;
- seeds;
- anonimización;
- ambientes aislados;
- reset automático.

## Reglas

- no usar datos productivos sin anonimización;
- no incluir secretos;
- mantener datasets versionados;
- permitir reproducción;
- separar datos por marca;
- documentar supuestos.

---

# 23. Environments

| Environment | Uso |
| --- | --- |
| Local | Desarrollo rápido |
| Test | Automatización |
| Integration | Servicios reales |
| Staging | Validación preproducción |
| Production | Operación real |

## Requisitos

- configuraciones separadas;
- secretos separados;
- bases separadas;
- observabilidad;
- datos controlados;
- pipelines reproducibles.

---

# 24. CI/CD Quality Gates

## Pull Request

Debe ejecutar:

1. lint;
2. formatting check;
3. unit tests;
4. integration tests críticas;
5. coverage;
6. static analysis;
7. dependency scan;
8. secret scan;
9. build;
10. contract validation.

## Main branch

Debe ejecutar:

1. suite completa;
2. SonarQube;
3. container scan;
4. database migration test;
5. E2E smoke;
6. artifact generation.

## Release

Debe ejecutar:

1. regression;
2. E2E completo;
3. performance smoke;
4. DAST;
5. deployment verification;
6. rollback validation;
7. release report.

---

# 25. SonarQube

## Objetivo

Centralizar métricas de calidad.

## Métricas

- bugs;
- vulnerabilities;
- code smells;
- coverage;
- duplications;
- maintainability;
- reliability;
- security hotspots;
- technical debt.

## Quality Gate inicial

| Métrica | Objetivo inicial |
| --- | --- |
| New code coverage | 70% o más |
| Duplicated lines | Menor a 5% |
| New critical bugs | 0 |
| New blocker bugs | 0 |
| New vulnerabilities | 0 críticas |
| Security hotspots | Revisados |
| Maintainability rating | A |
| Reliability rating | A |

## Evolución

El objetivo puede aumentar progresivamente a 80% de cobertura en módulos críticos.

---

# 26. Coverage Strategy

## Objetivo inicial

- cobertura general mínima: 70%;
- módulos críticos: 80% o más;
- lógica financiera: 90% o más;
- permisos y seguridad: 90% o más;
- agentes críticos: escenarios principales cubiertos;
- migrations: pruebas funcionales.

## Regla

La cobertura no reemplaza calidad de pruebas. Se debe medir qué comportamiento está realmente validado.

---

# 27. Test Naming

## Formato recomendado

```
test_<behavior>_<condition>_<expected_result>
```

## Ejemplos

```
test_create_product_with_valid_data_returns_201
test_create_product_without_permission_returns_403
test_price_calculation_with_missing_rate_raises_error
test_agent_requires_confirmation_before_write_operation
```

---

# 28. Bug Management

## Flujo

```
Detected
   ↓
Triaged
   ↓
Prioritized
   ↓
Assigned
   ↓
Fixed
   ↓
Verified
   ↓
Closed
```

## Severidad

| Nivel | Definición |
| --- | --- |
| Blocker | Impide operar |
| Critical | Riesgo alto o pérdida de datos |
| Major | Funcionalidad importante afectada |
| Minor | Impacto limitado |
| Trivial | Problema cosmético |

## Plataforma

Azure Boards será el sistema principal para bugs técnicos.

---

# 29. Regression Strategy

## Cuándo ejecutar

- cambios en modelos;
- cambios en serializers;
- cambios en contratos;
- cambios en auth;
- cambios en permisos;
- cambios en migraciones;
- cambios en tools;
- cambios en prompts;
- cambios en infraestructura;
- antes de release.

## Automatización

Las regresiones críticas deben formar parte del pipeline.

---

# 30. Resilience Testing

## Casos

- PostgreSQL no disponible;
- Redis no disponible;
- Kafka no disponible;
- Qdrant no disponible;
- LLM no disponible;
- API externa lenta;
- timeout;
- respuesta inválida;
- pérdida de red;
- worker caído;
- mensaje duplicado;
- evento fuera de orden.

## Controles

- retries;
- circuit breaker;
- timeout;
- fallback;
- idempotencia;
- dead-letter queue;
- alertas;
- graceful degradation.

---

# 31. QA Metrics

| Métrica | Objetivo |
| --- | --- |
| Test pass rate | Porcentaje de pruebas exitosas |
| Coverage | Cobertura |
| Defect density | Bugs por módulo |
| Escaped defects | Bugs encontrados después de release |
| Mean time to detect | Tiempo de detección |
| Mean time to repair | Tiempo de corrección |
| Flaky test rate | Inestabilidad de pruebas |
| Build success rate | Estabilidad CI |
| Regression rate | Cambios que rompen funcionalidades |
| API contract failures | Incompatibilidades |
| Performance regression | Degradación |
| Security findings | Vulnerabilidades |

---

# 32. Flaky Tests

## Objetivo

Evitar pruebas inestables.

## Controles

- controlar tiempo;
- controlar datos;
- evitar dependencias externas;
- limpiar estado;
- usar waits explícitos;
- evitar sleep fijo;
- registrar logs;
- aislar concurrencia;
- reintentar solo para diagnóstico, no ocultar errores.

---

# 33. QA Documentation

Cada repositorio debe documentar:

- cómo ejecutar pruebas;
- estructura;
- dependencias;
- cobertura;
- fixtures;
- datos;
- comandos;
- troubleshooting;
- Quality Gate;
- tipos de pruebas;
- pipeline.

---

# 34. Reporting

## Reportes generados

- cobertura;
- SonarQube;
- pruebas unitarias;
- integración;
- E2E;
- performance;
- seguridad;
- contratos;
- AI evaluation;
- release verification.

## Destinos

- Azure Pipelines;
- Jenkins;
- GitHub Actions;
- Azure DevOps dashboards;
- Grafana;
- README;
- Wiki.

---

# 35. Roadmap de implementación

## Etapa 1 — Base inmediata

1. configurar pytest en `sbm-api`;
2. configurar pytest en `dp-api`;
3. configurar Vitest en `sbm-manager`;
4. agregar cobertura;
5. implementar factories;
6. probar `product`;
7. probar `material`;
8. configurar SonarQube;
9. definir Quality Gate.

## Etapa 2 — Integración

1. Testcontainers;
2. pruebas PostgreSQL;
3. pruebas de contratos;
4. pruebas entre APIs;
5. Bruno o Postman versionado;
6. Newman;
7. Playwright smoke.

## Etapa 3 — Seguridad y CI/CD

1. SAST;
2. dependency scanning;
3. secret scanning;
4. container scanning;
5. DAST;
6. gates en PR;
7. reportes automáticos.

## Etapa 4 — Distribuido

1. Redis;
2. Celery;
3. Kafka;
4. idempotencia;
5. resilience testing;
6. performance;
7. observabilidad.

## Etapa 5 — IA

1. RAG evaluation;
2. tool testing;
3. agent testing;
4. prompt regression;
5. red teaming;
6. AI observability.

---

# 36. Prioridad actual

## Urgente

1. estándar pytest;
2. factories;
3. pruebas de `product`;
4. pruebas de `material`;
5. cobertura;
6. SonarQube;
7. Quality Gate;
8. API tests;
9. integración DB;
10. Playwright smoke.

## Corto plazo

1. contract testing;
2. Testcontainers;
3. CI/CD;
4. security testing;
5. regression suite;
6. performance baseline.

## Mediano plazo

1. Kafka testing;
2. Celery testing;
3. Kubernetes testing;
4. AI evaluation;
5. agent testing;
6. resilience testing.

---

# 37. Criterio de finalización

Una funcionalidad se considera terminada cuando:

1. cumple criterios de aceptación;
2. tiene pruebas unitarias;
3. tiene integración cuando corresponde;
4. tiene cobertura suficiente;
5. supera Quality Gate;
6. supera análisis de seguridad;
7. tiene documentación;
8. tiene manejo de errores;
9. tiene observabilidad cuando corresponde;
10. puede demostrarse de extremo a extremo.

---

# 38. Definición de Done

```
Implemented
   +
Tested
   +
Reviewed
   +
Secure
   +
Documented
   +
Observable
   +
Deployable
```

Una tarea no está terminada solo porque el código funciona localmente. Debe poder mantenerse, validarse, desplegarse y operar de forma confiable.