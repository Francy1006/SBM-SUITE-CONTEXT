# 🔐 Security & DevSecOps

> Estrategia transversal de seguridad para SBM Suite.
> 
> 
> Esta página define cómo integrar seguridad desde el diseño hasta producción, cubriendo aplicaciones, APIs, datos, contenedores, Kubernetes, CI/CD, agentes IA, RAG, dependencias e infraestructura.
> 
> La seguridad no se considera una revisión final. Debe formar parte del desarrollo, QA, despliegue, operación y monitoreo.
> 

---

# 1. Objetivo

Establecer un modelo DevSecOps para SBM Suite que permita:

- prevenir vulnerabilidades;
- proteger datos empresariales;
- controlar acceso por usuario, rol y marca;
- detectar secretos expuestos;
- validar dependencias;
- escanear código e imágenes;
- proteger APIs;
- asegurar contenedores y Kubernetes;
- evaluar riesgos de agentes IA;
- integrar controles dentro de CI/CD;
- generar evidencia verificable para el portafolio.

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
- Redis;
- Celery;
- Kafka;
- PostgreSQL;
- Docker;
- Kubernetes;
- Azure DevOps;
- Jenkins;
- GitHub;
- n8n;
- integraciones externas;
- agentes IA;
- MCP;
- RAG;
- modelos ML;
- pipelines CI/CD.

---

# 3. Principios

1. **Security by design**
    
    La seguridad comienza en arquitectura y diseño.
    
2. **Least privilege**
    
    Cada usuario, servicio y agente recibe solo los permisos mínimos.
    
3. **Zero trust**
    
    Ningún servicio, canal o usuario se considera confiable por defecto.
    
4. **Defense in depth**
    
    Se aplican múltiples capas de protección.
    
5. **Secure defaults**
    
    Las configuraciones iniciales deben ser restrictivas.
    
6. **Shift-left security**
    
    Los controles se ejecutan antes del despliegue.
    
7. **Continuous verification**
    
    La seguridad se valida de forma recurrente.
    
8. **Auditability**
    
    Toda acción relevante debe dejar trazabilidad.
    
9. **Human approval**
    
    Las acciones críticas requieren confirmación.
    
10. **Free and self-hosted first**
    
    Para el portafolio se priorizan herramientas gratuitas, locales u open source.
    

---

# 4. Modelo DevSecOps

```
Plan
  ↓
Threat Modeling
  ↓
Development
  ↓
SAST
  ↓
Dependency and Secret Scanning
  ↓
Testing
  ↓
Container and IaC Scanning
  ↓
Deployment
  ↓
DAST
  ↓
Runtime Monitoring
  ↓
Incident Response
```

---

# 5. Marcos de referencia

| Standard | Uso |
| --- | --- |
| OWASP Top 10 | Riesgos web |
| OWASP API Security Top 10 | Riesgos en APIs |
| OWASP Top 10 for LLM Applications | Riesgos en IA generativa |
| CIS Benchmarks | Hardening de sistemas |
| NIST Cybersecurity Framework | Gobierno general |
| STRIDE | Threat modeling |
| MITRE ATT&CK | Modelado de técnicas de ataque |
| CWE | Clasificación de debilidades |
| CVSS | Severidad de vulnerabilidades |

---

# 6. Threat Modeling

## Objetivo

Identificar amenazas antes de implementar o desplegar.

## Metodología

Se utilizará STRIDE:

| Categoría | Ejemplo |
| --- | --- |
| Spoofing | Suplantación de usuario |
| Tampering | Modificación de datos |
| Repudiation | Acciones sin trazabilidad |
| Information Disclosure | Exposición de información |
| Denial of Service | Saturación de servicios |
| Elevation of Privilege | Escalada de permisos |

## Activos críticos

- credenciales;
- datos de clientes;
- datos por marca;
- precios;
- inventario;
- documentos;
- información financiera;
- tokens de integraciones;
- prompts;
- memoria de agentes;
- embeddings;
- configuraciones;
- infraestructura.

---

# 7. Identity and Access Management

## Objetivo

Controlar acceso de forma centralizada y trazable.

## Requisitos

- autenticación robusta;
- autorización por rol;
- control por marca;
- permisos por módulo;
- separación entre usuarios internos y externos;
- sesiones con expiración;
- revocación;
- auditoría;
- soporte futuro para MFA;
- soporte futuro para SSO.

## Tecnologías

- OAuth 2.0;
- OpenID Connect;
- JWT;
- sesiones seguras;
- RBAC;
- permisos por recurso;
- políticas por marca.

---

# 8. Seguridad por marca

## Principio

Un usuario o agente no debe acceder a información de otra marca sin autorización explícita.

## Controles

- `brand_id` o scope equivalente;
- validación en backend;
- filtros obligatorios;
- permisos en cada endpoint;
- pruebas de aislamiento;
- logs de acceso;
- separación lógica;
- validación en RAG;
- validación en tools;
- validación en agentes.

---

# 9. API Security

## Riesgos

- broken object level authorization;
- broken authentication;
- excessive data exposure;
- mass assignment;
- injection;
- rate abuse;
- improper inventory management;
- SSRF;
- misconfiguration.

## Controles

- autenticación;
- autorización;
- validación de schemas;
- serializers restrictivos;
- paginación;
- filtros controlados;
- rate limiting;
- timeouts;
- idempotencia;
- CORS restrictivo;
- headers de seguridad;
- versionado;
- logs;
- protección contra brute force.

---

# 10. Web Security

## Controles

- HTTPS obligatorio;
- HSTS;
- Content Security Policy;
- X-Content-Type-Options;
- Referrer-Policy;
- Permissions-Policy;
- secure cookies;
- HttpOnly;
- SameSite;
- CSRF protection;
- XSS prevention;
- input validation;
- output encoding.

---

# 11. Secrets Management

## Riesgos

- secretos en repositorios;
- `.env` publicados;
- tokens en logs;
- credenciales embebidas;
- secretos compartidos;
- falta de rotación.

## Herramientas

| Tool | Uso |
| --- | --- |
| Doppler Free | Gestión de secretos |
| Gitleaks | Detección en Git |
| TruffleHog OSS | Detección avanzada |
| Environment Variables | Configuración runtime |
| Kubernetes Secrets | Secretos en cluster |
| Azure DevOps Variable Groups | Variables seguras |

## Reglas

- no versionar secretos;
- no imprimir secretos;
- rotar credenciales;
- separar secretos por entorno;
- usar permisos mínimos;
- auditar acceso;
- revocar inmediatamente ante exposición.

---

# 12. Static Application Security Testing

## Herramientas

| Tool | Uso |
| --- | --- |
| Semgrep Community | SAST multilenguaje |
| Bandit | Seguridad Python |
| ESLint Security Plugins | Seguridad JavaScript |
| SonarQube Community Build | Calidad y security hotspots |

## Reglas

- ejecutar en pull requests;
- bloquear hallazgos críticos;
- revisar falsos positivos;
- mantener reglas versionadas;
- documentar excepciones.

---

# 13. Dependency Security

## Herramientas

- pip-audit;
- npm audit;
- Dependabot;
- OWASP Dependency-Check;
- Trivy;
- CycloneDX.

## Controles

- inventario de dependencias;
- actualización regular;
- bloqueo por vulnerabilidades críticas;
- SBOM;
- revisión de licencias;
- versiones fijadas;
- eliminación de librerías sin uso.

---

# 14. Software Supply Chain

## Objetivo

Proteger código, dependencias, imágenes y artefactos.

## Controles

- repositorios protegidos;
- branch protection;
- revisión obligatoria;
- firmas cuando corresponda;
- artefactos versionados;
- SBOM;
- imágenes inmutables;
- registros privados;
- control de provenance;
- escaneo antes de publicar.

---

# 15. Container Security

## Herramientas

- Trivy;
- Docker Scout como alternativa opcional;
- Hadolint;
- Dockle como alternativa futura.

## Controles

- imágenes mínimas;
- usuarios no root;
- multi-stage builds;
- versiones fijas;
- sin secretos en capas;
- health checks;
- filesystem read-only cuando sea posible;
- capabilities mínimas;
- escaneo de imágenes;
- reducción de puertos expuestos.

---

# 16. Kubernetes Security

## Herramientas

| Tool | Uso |
| --- | --- |
| Kubescape | Evaluación del cluster |
| kube-bench | CIS Benchmark |
| kube-score | Validación de manifests |
| Trivy | Escaneo IaC e imágenes |
| Falco | Runtime security |

## Controles

- RBAC;
- namespaces;
- Network Policies;
- Pod Security Standards;
- Secrets;
- resource limits;
- non-root containers;
- read-only filesystem;
- liveness y readiness;
- service accounts dedicadas;
- ingress seguro;
- TLS;
- audit logs.

---

# 17. Infrastructure as Code Security

## Herramientas

- Trivy;
- Checkov como alternativa;
- tfsec como alternativa;
- kube-score;
- Kubescape.

## Alcance

- Terraform;
- Kubernetes manifests;
- Helm;
- Docker Compose;
- Dockerfiles;
- Azure Pipelines;
- Jenkinsfiles.

---

# 18. Dynamic Application Security Testing

## Herramientas

| Tool | Uso |
| --- | --- |
| OWASP ZAP | DAST automatizado |
| Burp Suite Community | Pruebas manuales |
| Nuclei | Escaneo basado en templates |

## Uso

- entornos de test o staging;
- APIs;
- aplicaciones web;
- smoke security tests;
- validación antes de release.

---

# 19. Network Security

## Herramientas

- Nmap;
- Wireshark;
- TLS scanners;
- firewall local;
- Network Policies;
- reverse proxy.

## Controles

- puertos mínimos;
- segmentación;
- TLS;
- acceso administrativo restringido;
- bases de datos no públicas;
- monitoreo;
- rate limiting;
- protección de endpoints internos.

---

# 20. Database Security

## Controles

- usuarios separados;
- permisos mínimos;
- conexiones cifradas;
- backups protegidos;
- auditoría;
- rotación de credenciales;
- restricciones de red;
- validación de queries;
- protección contra SQL injection;
- cifrado de datos sensibles;
- restauración probada.

---

# 21. Logging and Audit

## Eventos auditables

- login;
- logout;
- cambios de permisos;
- operaciones críticas;
- cambios de precios;
- eliminaciones;
- emisión de documentos;
- acciones de agentes;
- tool calls;
- cambios de configuración;
- despliegues;
- acceso a datos sensibles.

## Reglas

- logs estructurados;
- correlation IDs;
- timestamps;
- identidad del actor;
- marca;
- resultado;
- origen;
- sin secretos ni datos sensibles innecesarios.

---

# 22. AI and LLM Security

## Riesgos

- prompt injection;
- indirect prompt injection;
- data leakage;
- tool abuse;
- privilege escalation;
- insecure output handling;
- excessive agency;
- malicious documents;
- cross-brand leakage;
- insecure memory;
- model denial of service.

## Controles

- allowlist de tools;
- permisos por agente;
- validación de inputs;
- validación de outputs;
- filtros de contexto;
- aislamiento por marca;
- human approval;
- rate limits;
- timeouts;
- sandboxing;
- red teaming;
- auditoría.

## Herramientas

- OWASP Top 10 for LLM Applications;
- Garak;
- Promptfoo OSS;
- Ragas;
- DeepEval;
- Guardrails AI;
- Langfuse.

---

# 23. RAG Security

## Riesgos

- documentos maliciosos;
- recuperación de contenido no autorizado;
- información desactualizada;
- manipulación del índice;
- fuga entre marcas;
- inyección indirecta.

## Controles

- metadata obligatoria;
- filtros por usuario y marca;
- `is_active=true`;
- control de versiones;
- fuentes autorizadas;
- sanitización;
- validación de retrieval;
- citas;
- auditoría;
- pruebas de acceso cruzado.

---

# 24. Agent Security

Cada agente debe tener:

- objetivo definido;
- tools autorizadas;
- permisos mínimos;
- scope de marca;
- límites;
- timeout;
- retries;
- aprobación humana;
- auditoría;
- estrategia de fallback.

## Regla

Ningún agente debe:

- acceder directamente a la base de datos;
- ejecutar código arbitrario;
- modificar infraestructura sin aprobación;
- publicar contenido crítico sin confirmación;
- realizar transacciones financieras autónomas;
- ampliar sus propios permisos.

---

# 25. MCP Security

## Controles

- servidores MCP autorizados;
- autenticación;
- permisos por tool;
- validación de recursos;
- aislamiento;
- logs;
- límites;
- revisión de servidores externos;
- no exponer secretos;
- no conectar MCP desconocidos a producción.

---

# 26. OpenClaw Security

## Uso

OpenClaw se considera un gateway multicanal opcional.

## Controles obligatorios

- aislamiento;
- permisos mínimos;
- canales autorizados;
- autenticación;
- rate limiting;
- logs;
- no acceso directo a base de datos;
- no acceso directo a infraestructura;
- acceso solo mediante `SBM-AI-ASSISTANT`;
- tools restringidas;
- revisión de configuración.

---

# 27. CI/CD Security Gates

## Pull Request

Debe ejecutar:

1. SAST;
2. secret scanning;
3. dependency scanning;
4. lint;
5. tests;
6. coverage;
7. SonarQube;
8. IaC scanning cuando corresponda.

## Main

Debe ejecutar:

1. build;
2. image scan;
3. SBOM;
4. integration tests;
5. migration tests;
6. artifact validation.

## Release

Debe ejecutar:

1. DAST;
2. container scan;
3. configuration review;
4. deployment validation;
5. rollback verification;
6. security report.

---

# 28. Security Severity

| Severity | Acción |
| --- | --- |
| Critical | Bloqueo inmediato |
| High | Corrección antes de release |
| Medium | Plan de corrección |
| Low | Backlog y seguimiento |
| Informational | Revisión |

---

# 29. Vulnerability Management

## Flujo

```
Detect
  ↓
Validate
  ↓
Classify
  ↓
Prioritize
  ↓
Remediate
  ↓
Retest
  ↓
Close
```

## Registro

Azure Boards será el sistema principal para vulnerabilidades técnicas.

---

# 30. Incident Response

## Etapas

1. detección;
2. contención;
3. erradicación;
4. recuperación;
5. análisis;
6. documentación;
7. mejora preventiva.

## Incidentes contemplados

- credencial expuesta;
- acceso no autorizado;
- fuga de datos;
- dependencia comprometida;
- imagen vulnerable;
- prompt injection;
- abuso de agente;
- servicio comprometido;
- malware;
- indisponibilidad.

---

# 31. Backup and Recovery Security

## Controles

- backups cifrados;
- accesos restringidos;
- retención definida;
- pruebas de restauración;
- separación de entornos;
- inventario;
- logs;
- copias fuera del entorno principal cuando corresponda.

---

# 32. Privacy and Data Protection

## Principios

- minimización;
- finalidad;
- acceso controlado;
- retención;
- eliminación;
- anonimización;
- pseudonimización;
- consentimiento cuando corresponda;
- trazabilidad.

## Datos sensibles

- información personal;
- información financiera;
- credenciales;
- contratos;
- documentos;
- historial de clientes;
- información por marca.

---

# 33. Security Testing

Debe incluir:

- pruebas de autenticación;
- pruebas de autorización;
- pruebas de aislamiento por marca;
- pruebas de input validation;
- pruebas de rate limiting;
- pruebas de CORS;
- pruebas de secrets;
- pruebas DAST;
- pruebas de agentes;
- pruebas de RAG;
- pruebas de APIs;
- pruebas de contenedores.

---

# 34. Tooling Prioritario

## Inmediato

| Tool | Prioridad |
| --- | --- |
| SonarQube Community Build | Alta |
| Semgrep Community | Alta |
| Bandit | Alta |
| pip-audit | Alta |
| npm audit | Alta |
| Gitleaks | Alta |
| Trivy | Alta |
| OWASP ZAP | Alta |

## Corto plazo

| Tool | Prioridad |
| --- | --- |
| Burp Suite Community | Media-alta |
| OWASP Dependency-Check | Media-alta |
| Kubescape | Media-alta |
| kube-bench | Media |
| kube-score | Media |
| Falco | Media |
| Garak | Media-alta |
| Promptfoo | Media-alta |

---

# 35. Security Metrics

| Métrica | Objetivo |
| --- | --- |
| Critical vulnerabilities | 0 |
| High vulnerabilities | 0 antes de release |
| Secrets exposed | 0 |
| Dependency age | Controlada |
| Mean time to remediate | Reducir progresivamente |
| Security tests passing | 100% |
| Unauthorized access attempts | Monitoreados |
| Security hotspots reviewed | 100% |
| Container scan failures | 0 críticas |
| Agent actions audited | 100% |

---

# 36. Security Documentation

Cada repositorio debe incluir:

- modelo de amenazas;
- secretos necesarios;
- permisos;
- endpoints sensibles;
- controles;
- herramientas;
- comandos;
- excepciones;
- incidentes conocidos;
- proceso de actualización;
- checklist de release.

---

# 37. Roadmap de implementación

## Etapa 1 — Base inmediata

1. SonarQube;
2. Semgrep;
3. Bandit;
4. pip-audit;
5. npm audit;
6. Gitleaks;
7. Trivy;
8. revisión de `.env`;
9. headers de seguridad;
10. permisos por endpoint.

## Etapa 2 — CI/CD

1. gates en PR;
2. dependency scanning;
3. secret scanning;
4. container scanning;
5. SBOM;
6. reportes automáticos.

## Etapa 3 — Aplicaciones y APIs

1. OWASP ZAP;
2. Burp Community;
3. rate limiting;
4. auditoría;
5. threat modeling;
6. aislamiento por marca.

## Etapa 4 — Kubernetes

1. Kubescape;
2. kube-bench;
3. kube-score;
4. RBAC;
5. Network Policies;
6. Falco.

## Etapa 5 — IA

1. OWASP LLM Top 10;
2. Promptfoo;
3. Garak;
4. tool authorization;
5. RAG access control;
6. human approval;
7. red teaming.

---

# 38. Prioridad actual

## Urgente

1. inventario de secretos;
2. Gitleaks;
3. Semgrep;
4. Bandit;
5. dependency scanning;
6. Trivy;
7. SonarQube;
8. permisos por marca;
9. headers y CORS;
10. documentación de amenazas.

## Corto plazo

1. ZAP;
2. Burp Community;
3. SBOM;
4. CI/CD gates;
5. Kubernetes scanning;
6. auditoría centralizada.

## Mediano plazo

1. Falco;
2. seguridad Kafka;
3. seguridad Celery;
4. seguridad MCP;
5. seguridad OpenClaw;
6. red teaming de agentes.

---

# 39. Criterio de finalización

Una funcionalidad se considera segura cuando:

1. tiene threat model;
2. aplica least privilege;
3. valida entradas;
4. protege datos;
5. tiene pruebas de seguridad;
6. no expone secretos;
7. supera SAST;
8. supera dependency scanning;
9. supera container scanning cuando corresponde;
10. tiene logs y auditoría;
11. tiene documentación;
12. tiene plan de respuesta ante fallas.

---

# 40. Definición de Secure Done

```
Designed Securely
      +
Implemented Safely
      +
Tested Continuously
      +
Scanned Automatically
      +
Audited
      +
Documented
      +
Monitored
```

La seguridad de SBM Suite debe demostrarse mediante controles reales, reportes, pruebas y trazabilidad; no solo mediante declaraciones de diseño.

---

# 41. Multi-brand/application security baseline — 2026-08-16

Authorization expands through SBM User → Franchise/Brand User → Client/User → Customer/User when applicable. PC patient/health data is restricted; CG documents/plans and KS device/camera access require object-level controls.

Security is implemented as a governed cell: `Batman Agent` leads; `Joker Agent` performs authorized Red Team/pentesting; `Queen Agent` manages the security lab/tools; Alfred/Robin/Gotham/Darth Maul/Cerberus/Hercules cover requirements, integrity, drift, threat hunting, quarantine and sanitization. `Snape Agent` remains an independent `sbm-admin` auditor outside Batman's operational chain.

```text
Development → QA PASS → named Security agents → SBM-SECURITY-API (Go/Gin/PostgreSQL)
→ local/docker/external tools → findings/evidence/mitigation/prevention/regression controls
→ SBM-SECURITY human review → APPROVE release | REJECT Development
```

Initial tool coverage: `Semgrep ; Trivy ; Gitleaks ; OWASP ZAP ; Nuclei ; Nmap ; OSV-Scanner ; SSL Labs ; HTTP Observatory ; SecurityHeaders ; OSV API ; VirusTotal API`. Cadence supports hourly, daily, weekly, monthly and release-triggered checks. `SBM-CORE` schedules jobs/retries only and never owns Security policy/findings/evidence. SonarQube remains QA infrastructure and is not required as a permanent production service.

Relevant objectives: `OBJ-CTX-008`, `OBJ-CTX-009`, `OBJ-CTX-019`, `OBJ-CTX-040`.
