# SECURITY_CONTEXT.md

> **Last updated:** 2026-08-16
>
> **Purpose**
>
> Persistent transversal security context for **SBM Suite**. It defines security objectives, assets, trust boundaries, authentication, authorization, tenant isolation, secrets management, secure development, validation, vulnerabilities, audit, incident response and security roadmap.
>
> **Accuracy note**
>
> Only verified controls, risks and evidence may be marked as implemented or validated. Unknown states remain `N/A`.

## 1. Security overview

SBM Suite applies security across:

- frontend applications;
- client-facing APIs;
- internal platform APIs;
- database access;
- AI orchestration;
- context and documentation workflows;
- CI/CD and QA tooling;
- local and cloud infrastructure.

Core principle:

```text
identity
→ tenant or franchise
→ active modules
→ role
→ permission
→ restriction
→ requested object
→ validated action
```

No component may bypass this chain.

## 2. Security objectives

1. Preserve tenant and brand isolation.
2. Enforce least privilege.
3. Separate client and internal platform operations.
4. Prevent secret exposure.
5. Preserve auditability.
6. Protect business and personal data.
7. Prevent direct AI access to PostgreSQL.
8. Validate all external inputs.
9. Secure context and documentation ZIP workflows.
10. Detect vulnerabilities and insecure dependencies.
11. Support controlled incident response.
12. Preserve security evidence in QA contexts.

## 3. Assets and trust boundaries

| Asset | Owner | Classification | Trust boundary | Main risk |
|---|---|---|---|---|
| Brand/client/customer business data | Brand / client | confidential/restricted | Responsible brand API and PostgreSQL | cross-brand/client/customer access |
| Platform configuration | SBM | restricted | SBM-API | unauthorized administration |
| Credentials and tokens | Service owner | secret | environment and secret stores | leakage or misuse |
| Context files | SBM-SUITE | internal | Git and context workflow | unauthorized modification |
| Documentation files | SBM-SUITE | internal | Git and documentation workflow | stale or malicious content |
| Vector indexes | SBM-AI-ASSISTANT | internal | Qdrant | data mixing or stale retrieval |
| Audit logs | Component owner | restricted | logging platform | tampering or sensitive leakage |
| QA and SonarQube evidence | Project owner | internal | QA workflow | false validation claims |

Trust boundaries include:

- browser to API;
- client API to database;
- internal API to database;
- AI assistant to Tools;
- Tool to API;
- context ZIP to upgrade service;
- documentation ZIP to upgrade service;
- local environment to cloud services.

## 4. Authentication

Authentication rules:

- all protected APIs require authenticated identities;
- internal and client identities must remain distinguishable;
- expired, invalid or missing credentials must be rejected;
- technical credentials must not be treated as user credentials;
- AI-triggered actions must preserve the requesting user identity;
- authentication errors must not expose internal details.

Current mechanisms must be documented per project when verified.

## 5. Authorization

Authorization must evaluate:

```text
identity
→ tenant
→ module
→ role
→ permission
→ restriction
→ object
→ action
```

Rules:

- deny by default;
- enforce object-level authorization;
- prevent privilege escalation;
- separate client and internal administration permissions;
- do not authorize based only on frontend visibility;
- every write must pass backend authorization;
- AI Tools must use the same authorization rules as direct API calls.

## 6. Roles and permissions

| Role type | Scope | Allowed responsibility | Prohibited responsibility |
|---|---|---|---|
| SBM User | Platform | Provisioning, governance, subscriptions, shared services and internal administration | Unauthorized brand/client business operations |
| Franchise/Brand User | One franchise/brand | Brand operations and approved client/business management | Other brands or platform administration |
| Client User | One client within one brand | Client-specific workflows/assets/documents/schedules/inventory exposed by brand | Other clients, brand administration, platform controls |
| Customer User | Own customer/beneficiary scope when customer login exists | Purchase/schedule/confirm/status actions explicitly exposed | Client/brand administration and unrelated customer data |
| Service account | Technical integration | Explicit machine-to-machine actions | Human privilege inheritance |
| AI-assisted caller | Inherited caller scope | Approved Tool/agent operations | Independent authority |

`franchise` remains the current database scope name for the brand boundary.

## 7. Tenant and brand isolation

Mandatory protections apply at every relevant level:

- franchise/brand-scoped queries and writes;
- client-scoped queries/writes/exports;
- customer/object-scoped access when customer channels exist;
- scope propagation through caches, queues, events, jobs and AI Tool calls;
- tenant-safe logs/vector indexes;
- separation of internal/platform data from brand business data.

Required negative cases include Brand A → Brand B, Client A → Client B and Customer A → Customer B access attempts. These are risk level `5` and must be denied/hidden according to the API contract.

## 8. Secrets management

Rules:

1. Never commit `.env` files with secret values.
2. Never include credentials in ZIP packages.
3. Never log passwords, tokens or database credentials.
4. Use environment variables or approved secret stores.
5. Separate development, staging and production secrets.
6. Rotate exposed credentials immediately.
7. Restrict service credentials by scope.
8. Do not embed secrets in fixtures, scripts or documentation.
9. Secret values must not enter Qdrant.
10. Generated manifests may reference secret names, never values.

## 9. Data protection

Controls:

- classify sensitive data;
- minimize collected data;
- restrict personal data access;
- use encrypted transport;
- protect backups;
- preserve integrity;
- prevent unauthorized export;
- apply retention and deletion rules;
- avoid sensitive content in logs and embeddings.

Detailed ownership and lifecycle belong in `DATA_CONTEXT.md`.

## 10. Network security

Rules:

- expose only required ports;
- separate internal and public services;
- validate Docker network membership;
- restrict database access to approved services;
- use TLS outside trusted local environments;
- avoid permissive production CORS;
- define timeout and retry behavior;
- protect internal APIs from public exposure;
- document firewall and ingress rules when deployed.

Known local shared network:

```text
sbm-network
```

## 11. Dependency security

Required controls:

- dependency inventory;
- vulnerability scanning;
- supported runtime versions;
- removal of unused dependencies;
- lockfiles where applicable;
- reviewed upgrades;
- critical vulnerability remediation;
- license review when required;
- container image scanning;
- trusted package sources.

No dependency is considered secure without current evidence.

## 12. Secure development lifecycle

Security must be integrated into:

```text
objective definition
→ branch creation
→ implementation
→ focused tests
→ qa-check.sh
→ coverage and SonarQube
→ context-deploy
→ reviewed context update
→ documentation update
→ Git review
```

Required practices:

- least-privilege design;
- input validation;
- safe error handling;
- code review;
- security tests;
- dependency scanning;
- secret scanning;
- documented risks;
- rollback planning;
- auditability.

## 13. Security testing

Required security tests include:

- unauthenticated access;
- invalid credentials;
- expired credentials;
- unauthorized roles;
- object-level permission failures;
- cross-tenant access;
- module restrictions;
- privilege escalation;
- malformed input;
- path traversal;
- ZIP bombs where applicable;
- symlink rejection;
- absolute path rejection;
- unauthorized file replacement;
- secret leakage;
- direct database access attempts by AI;
- insecure error messages.

Security results belong in project and global QA contexts.

## 14. Vulnerability management

| Vulnerability ID | Project | Description | Severity | Status | Owner | Due date | Evidence |
|---|---|---|---:|---|---|---|---|
| N/A | N/A | No current vulnerability inventory supplied | 0 | unknown | N/A | N/A | No evidence supplied |

Severity scale:

```text
0 = none
1 = very low
2 = low
3 = medium
4 = high
5 = critical
```

Rules:

- critical and high vulnerabilities block release unless formally accepted;
- every accepted risk requires owner and mitigation;
- vulnerability status must come from evidence;
- do not delete historical vulnerability records without preserving resolution evidence.

## 15. Logging and audit

Audit events should include:

- request or correlation ID;
- timestamp;
- user or service identity;
- tenant or brand;
- component;
- endpoint or Tool;
- action;
- target object;
- result;
- error category;
- non-sensitive diagnostic message.

Logs must not expose:

- passwords;
- tokens;
- secrets;
- unrestricted personal data;
- database credentials;
- full sensitive payloads.

Audit records must be tamper-resistant according to environment capabilities.

## 16. Incident response

Minimum process:

```text
detect
→ classify
→ contain
→ preserve evidence
→ eradicate
→ recover
→ communicate
→ review
→ update controls
```

Required incident fields:

| Field | Requirement |
|---|---|
| Incident ID | mandatory |
| Date and time | mandatory |
| Severity | 0 to 5 |
| Affected projects | mandatory |
| Affected tenants or brands | mandatory when applicable |
| Description | mandatory |
| Containment action | mandatory |
| Evidence | mandatory |
| Owner | mandatory |
| Resolution | mandatory when closed |
| Follow-up actions | mandatory |

## 17. Security risks

| Risk ID | Domain | Description | Projects | Status | Evidence | Risk | Owner |
|---|---|---|---|---|---|---:|---|
| SEC-001 | Tenant isolation | Cross-tenant access if scope enforcement is incomplete | DP-API, SBM-API, SBM-AI-ASSISTANT | open | No complete transversal evidence | 5 | Project owners |
| SEC-002 | Secrets | Secret values may be exposed through environment, logs or generated packages | All | open | Manual controls only | 5 | Project owners |
| SEC-003 | AI authorization | AI Tools may lose requesting-user context | SBM-AI-ASSISTANT, APIs | open | Tool integration pending | 5 | SBM-AI-ASSISTANT |
| SEC-004 | ZIP processing | Malicious paths or symlinks could overwrite unauthorized files | Context and documentation workflows | open | Validation implementation pending | 5 | SBM-AI-ASSISTANT |
| SEC-005 | Internal API exposure | SBM-API operations could become reachable by unauthorized clients | SBM-API, SBM-MANAGER | open | Complete deployment evidence unavailable | 4 | SBM-API |
| SEC-006 | Dependency vulnerabilities | Outdated libraries or images may contain known vulnerabilities | All | open | Current scan evidence unavailable | 4 | Project owners |

## 18. Accepted exceptions

| Exception ID | Scope | Description | Risk | Reason | Owner | Expiration | Status |
|---|---|---|---:|---|---|---|---|
| N/A | N/A | No accepted security exceptions evidenced | 0 | N/A | N/A | N/A | none |

Exceptions require explicit approval and must never be inferred from missing evidence.

## 19. Security roadmap

| Priority | Objective | Status | Projects | Target date | Documentation |
|---:|---|---|---|---|---|
| 5 | Enforce and test tenant isolation | pending | DP-API, SBM-API, SBM-AI-ASSISTANT | N/A | Security and DevSecOps |
| 5 | Validate context and documentation ZIP security | pending | SBM-AI-ASSISTANT | N/A | Security and DevSecOps |
| 5 | Standardize secret handling and rotation | pending | All | N/A | Security and DevSecOps |
| 4 | Implement dependency and container scanning | pending | All | N/A | Security and DevSecOps |
| 4 | Define centralized audit and correlation IDs | pending | All | N/A | Observability |
| 4 | Define incident response workflow | pending | SBM Suite | N/A | Security and DevSecOps |
| 3 | Define production CORS, ingress and TLS rules | pending | APIs, frontend | N/A | DevOps / Cloud |

## 20. Related documentation

Relevant documentation paths must be recorded under:

```text
SBM-SUITE/context/documentation/
```

Related domains include:

- Security and DevSecOps;
- QA and Testing;
- Observability;
- DevOps;
- Cloud;
- Development;
- Roadmap;
- SBM Suite.

Specific page paths will be added when the documentation format is finalized.

## 21. Multi-brand and control-plane security baseline — 2026-08-16

Authorization must distinguish at minimum:

```text
SBM User
→ Franchise/Brand User
→ Client/User
→ Customer/User when applicable
```

`franchise` remains the current canonical brand scope in the database. Every API, mobile/store/client application, agent and asynchronous job must propagate the effective brand/client/customer scope rather than trusting frontend visibility.

Additional high-risk data/surfaces:

- `PC-CUSTOMER`: patient identity, health/prevision, appointments and QR confirmation are restricted data;
- CG documents/plans/SII information: object-level authorization, encrypted transport, controlled storage and audit are mandatory;
- KS camera/device integrations: authenticated device/client scope and explicit authorization are mandatory;
- `SBM-CONTROL`, `SBM-SECURITY` and `SBM-AI-MANAGER`: privileged control planes; deny-by-default, strong auth and full audit required;
- `SBM-CORE`: jobs/events must carry authorization/tenant context and use idempotency/retry controls without escalating privilege;
- `SBM-MARKETING`/`SBM-CONTENT`: social credentials, publication permissions and creative assets require separate secrets/access controls.

Security workflow target remains:

```text
implementation
→ QA
→ Batman/Joker security validation through SBM-SECURITY-API
→ human Security Gate in SBM-SECURITY when required
→ APPROVE: commit/release
→ REJECT: Development → QA → Security
```

`SBM-SECURITY` is the planned human UI/control plane for findings, scans, evidence, risks and approvals; `SBM-SECURITY-API` is the isolated Go/Gin/PostgreSQL backend; named Security agents live in `SBM-AI-ASSISTANT`.

SonarQube is treated as temporary QA/static-analysis infrastructure and is not required to run continuously in production.

### Autonomous Security cell and tooling

| Component | Responsibility |
|---|---|
| Batman Agent | Security leader/CISO/SOC orchestration, continuous posture and escalation |
| Alfred Agent | Security requirements, QA/CIA coordination and remediation follow-up |
| Robin Agent | Integrity, backups, data/document coherence |
| Gotham Agent | Drift between repositories, runtime, Context and Documentation |
| Joker Agent | Authorized Red Team and pentesting |
| Queen Agent | Security lab, tool/API environments and technical QA for Joker |
| Darth Maul Agent | Threat hunting and attribution using real/Joker indicators |
| Cerberus Agent | Hostile-by-default email/attachment quarantine and malware triage |
| Hercules Agent | Sanitization/normalization of validated content for downstream agents |
| Snape Agent | Independent `sbm-admin` audit of CEO/governance; outside Batman's operational chain |
| SBM-SECURITY-API | Go/Gin/PostgreSQL Security domain API and evidence owner |
| SBM-SECURITY | Human review/approval frontend |
| SBM-CORE | Scheduling/jobs/retries only; no Security policy/domain logic |

Local/Docker/open-source target tools: `Semgrep ; Trivy ; Gitleaks ; OWASP ZAP ; Nuclei ; Nmap ; OSV-Scanner`. External web/API integrations when free/authorized: `SSL Labs ; HTTP Observatory ; SecurityHeaders ; OSV API ; VirusTotal API ; SSL Labs API`. Notifications/integrations: `Slack ; Email ; Jira ; Git ; Documentation`.

```text
Hourly  → critical alerts/exposed surface/threat indicators/high-risk checks
Daily   → dependencies/secrets/containers/DAST deltas and unresolved critical/high findings
Weekly  → broader pentest/regression/threat-hunting and mitigation status
Monthly → posture report, trends, protocols and prevention plan
Release → QA PASS → Security Gate → approval/rejection
```

Pentest execution: Joker/Batman requests `SBM-SECURITY-API`; the API validates scope/policy; `SBM-CORE` schedules isolated work when asynchronous execution is needed; Queen-managed tools test only authorized targets; results/evidence return to `SBM-SECURITY-API`; agents correlate findings with business context, generate mitigation/prevention and a regression control when possible; `SBM-SECURITY` presents the final human gate.

## 22. Document boundary

This file defines transversal security architecture, controls, risks, testing expectations and roadmap.

It does not store:

- secret values;
- raw vulnerability reports;
- personal data;
- complete incident evidence;
- project-specific implementation details;
- deployment credentials;
- database schema definitions;
- detailed QA execution logs;
- documentation page content.

Detailed implementation and evidence remain in project contexts, QA artifacts, deployment contexts and security tooling.
