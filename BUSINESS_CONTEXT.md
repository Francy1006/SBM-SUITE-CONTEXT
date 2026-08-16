# BUSINESS_CONTEXT.md

> **Last updated:** 2026-08-16
>
> **Purpose**
>
> Persistent business context for **SBM Suite**. It defines brands, franchises, operational profiles, enabled modules, business domains, entities, rules and commercial boundaries.
>
> **Accuracy note**
>
> Business counts, module status and operational metrics must come from validated evidence or authoritative systems. Unknown values remain `N/A`.

## 1. Business overview

SBM Suite is a configurable ERP platform designed to support multiple businesses, brands, franchises and operational models from a shared technological ecosystem.

Core separation:

```text
Client business operation
→ client-facing application and API

Platform or contractual operation
→ internal SBM administration
```

The platform must reduce manual dependence on SBM personnel for routine client operations without exposing critical platform controls.

## 2. Product vision

Provide a multi-brand platform where each authorized business can operate independently while SBM retains control over:

- tenant and franchise provisioning;
- subscriptions and plans;
- contracted modules;
- global configuration;
- internal administration;
- shared platform services;
- platform-level audit and support.

## 3. Business actors

| Actor | Scope | Main responsibilities | Restrictions |
|---|---|---|---|
| SBM User | Platform | Provisioning, governance, global configuration, shared services and internal administration | Must not bypass brand/client ownership |
| Franchise/Brand User | One brand/franchise (`DP User`, `KS User`, `PC User`, `CG User`) | Operate the brand, its providers, catalogs, inventory, services, clients and approved workflows | No cross-brand or platform administration |
| Client User | One client of a brand | Operate client-specific inventory, documents, schedules, equipment or workflows exposed by that brand | No access to other clients or brand administration |
| Customer | Downstream person or organization served by a Client/brand; may authenticate when a customer channel exists | Consume/confirm services, appointments, purchases or status | Minimum required scope only |
| AI-assisted user | Inherited caller scope | Perform approved operations through Tools and responsible APIs | AI gains no independent authority |

Canonical hierarchy:

```text
SBM User
→ Franchise/Brand User
→ Client / Client User
→ Customer / Customer User when applicable
```

The database currently uses `franchise` as the canonical brand scope; that naming remains unchanged for now.

## 4. Brands and franchises

| Brand ID | Brand | Franchise | Description | Status | Source |
|---|---|---:|---|---|---|
| SBM | SBM | 0 | Platform owner, shared services and infrastructure | active | Suite context |
| DITALY-PASTA | Ditaly Pasta | 1 | Closed business with one year of real historical data; reference implementation for reusable brand logic | historical-reference | User-confirmed business state |
| KS | Kiseki Tech | 1 | Importer/seller of technology and innovation products; current production target | production-target | User-confirmed business model |
| PC | PortalConvenios.cl | 1 | Health/wellness operational coordination and hospital waiting-list referral services; current production target | production-target | User-confirmed business model |
| CG | Consorcio y Gestión | 1 | Commercial permits, sanitary resolutions, premises enablement and related procedures; current production target | production-target | User-confirmed business model |

Rules:

- `Franchise` uses `1 = true`, `0 = false` in this context convention.
- Every brand operates within isolated authorization/data boundaries.
- Ditaly historical data must be preserved and may be used as a reference/test dataset subject to security/privacy rules.
- KS, PC and CG are the current production-target brands.
- New brand repositories must be onboarded before being treated as implemented projects.

## 5. Brand operational profile

| Brand | Operational state | Production target | Historical/reference data | Current source |
|---|---|---:|---:|---|
| SBM | active platform | 1 | 1 | Suite context |
| Ditaly Pasta | closed | 0 | 1 | One year of real operating data retained |
| Kiseki Tech | active business / platform onboarding planned | 1 | 0 | User-confirmed business model |
| PortalConvenios.cl | active business / platform onboarding planned | 1 | 0 | User-confirmed business model |
| Consorcio y Gestión | active business / platform onboarding planned | 1 | 0 | User-confirmed business model |

Exact operational counts remain `N/A` until an authoritative endpoint/source is connected.

## 6. Enabled modules by brand

| Brand | Module | Enabled | Description | Effective date | Source |
|---|---|---:|---|---|---|
| Ditaly Pasta | Product | 1 | Sellable item management | N/A | Current validated domain |
| Ditaly Pasta | Material | 1 | Ingredient and operational input management | N/A | Current validated domain |
| Ditaly Pasta | Service | 1 | Non-physical business offering management | N/A | Current validated direction |
| Ditaly Pasta | Catalog | 1 | Grouping and publication of offerings | N/A | Current validated direction |
| Ditaly Pasta | Ticket | 1 | Client-facing operational and support requests | N/A | Current validated direction |
| Ditaly Pasta | Pricing | 1 | Price, tax and fiscal configuration | N/A | Current validated domain |
| Ditaly Pasta | Provider | 1 | Provider and related business information | N/A | Current validated domain |
| Ditaly Pasta | Branch | 1 | Physical or operational locations | N/A | Current validated domain |
| Ditaly Pasta | Agreement | 1 | Commercial relationship configuration | N/A | Current validated domain |

Rules:

- A module change updates this context when business capability changes.
- A technical implementation change alone does not change module status.
- Module activation remains platform-controlled when contractually applicable.

## 7. Core business domains

Canonical business domains:

```text
Product
Material
Service
Equipment        # planned database/domain addition
Catalog
Ticket
Package
Price
Provider
Branch
Agreement
Client
Customer
```

Core meanings:

- `Product`: purchased item intended for resale.
- `Material`: purchased item consumed/used operationally and not sold as the primary commercial item.
- `Service`: contracted or performed service, including third-party services, fees, commissions and logistics.
- `Equipment`: planned retained asset/fixed asset that may be used or rented; Kiseki rental/maintenance/spares remain long-term scope.
- `Catalog`: configurable commercial/acquisition composition (BOM/recipe) that may combine Product, Material, Service and Equipment with quantities/dosage.
- `Ticket`: sellable/reportable unit or scheduled commercial event exposed to the sales/channel layer.
- `Package`: mandatory item packaging/logistics association; Services use a special logical/non-physical package instead of `NULL`.

These domains remain independent even when they share common fields.

## 8. Business entities

| Entity | Description | Operational owner | Implementation state |
|---|---|---|---|
| Product | Purchased item intended for resale | Brand API | implemented in DP reference; planned for KS/PC/CG as applicable |
| Material | Purchased operational/production input not primarily sold | Brand API | implemented in DP reference; reusable |
| Service | Contracted/performed commercial or operational service | Brand API | implemented direction; extended semantics planned |
| Equipment | Retained asset/fixed asset, potentially rentable | Brand API | planned |
| Catalog | BOM/recipe/commercial composition joining item components and quantities | Brand API | existing concept; richer composition planned |
| Ticket | Unit sold/reported/scheduled by the commercial channel | Brand API | existing concept; semantics generalized |
| Package | Mandatory packaging/logistics classification for every item type, including logical Service package | Brand API / SBM-DB | existing concepts require canonicalization |
| Price | Versioned monetary state derived from base amount, rules, tax and currency | Brand API / sbm-calculation | existing + planned extension |
| Provider | Supplier/service provider | Brand API | existing |
| Branch | Physical/operational location | Brand API | existing |
| Agreement | Commercial relationship/conditions | Brand API | existing |
| Franchise | Canonical brand/business scope | SBM-API | existing |
| Client | Organization/person directly served/contracted by a brand | Brand API | existing/brand-specific evolution |
| Customer | Downstream beneficiary/end customer of a Client/brand | Brand API | planned generic model; required explicitly by PC |

SBM-DB remains the physical schema/migration authority for business tables.

## 9. Business rules

1. Users operate only within their authorized SBM/franchise/client/customer scope.
2. Routine brand/client operations should not require internal SBM intervention.
3. Product, Material, Service, Equipment, Catalog and Ticket remain separate capabilities.
4. Package is mandatory for item domains; Service uses a logical/non-physical package.
5. Catalog composes items/quantities/dosage but does not transfer lifecycle ownership of its components.
6. Ticket is the sellable/reportable/scheduled commercial unit; its exact lifecycle is brand-specific.
7. Each business capability has one canonical owner.
8. Price calculations/versioning remain backend responsibilities and must preserve currency/tax history.
9. Audit and confirmation metadata are server-controlled.
10. AI actions use the same permissions as direct user actions.
11. Frontends do not reproduce authoritative backend rules.
12. Platform provisioning remains internal.
13. Physical schema location does not determine business ownership.
14. Legacy/historical DP data must not be silently deleted or rewritten.
15. Cross-brand/client/customer access is prohibited unless explicitly designed.
16. Business capability changes must update this context and related documentation.

## 10. Commercial flows

Brand operation:

```text
Franchise/Brand User or Client User
→ approved manager/mobile/client/store channel
→ responsible brand API (DP reference; KS/PC/CG planned)
→ validated business operation
→ persisted business state
```

Internal platform operation:

```text
SBM User
→ SBM Manager / sbm-mobile / approved internal channel
→ SBM-API
→ identity, provisioning, authorization or global configuration
```

Customer operation when applicable:

```text
Customer
→ public/customer channel
→ responsible brand API
→ scoped purchase/schedule/confirmation/status operation
```

AI-assisted operation:

```text
Authorized caller
→ sbm-ai-assistant
→ explicit Tool / specialized agent
→ responsible API
→ validated result
```

The AI must not invent business identifiers, bypass validation or exceed the requesting caller's authority.

## 11. Pricing and fiscal concepts

A Price target may include:

- `base_net_amount`;
- calculated `net_amount`;
- VAT;
- additional taxes (including future category/international taxes where applicable);
- retention;
- `gross_amount`;
- source currency;
- exchange-rate reference/history;
- price configuration;
- referenced item;
- current-version state;
- confirmation/audit state.

Rules:

- `sbm-calculation` is the planned reusable financial/accounting calculation engine;
- brand APIs remain responsible for the business operation invoking those calculations;
- `sbm-util` may ingest authoritative exchange-rate observations such as USD and future EUR/UF;
- formula evaluation must be deterministic and monetary values use exact decimal handling;
- price/currency history must remain auditable; converted values are not silently overwritten;
- estimated/provisioned costs must remain distinguishable from actual paid/reconciled costs;
- frontends and agents must not duplicate authoritative fiscal/calculation logic.

## 12. Inventory and catalog concepts

Inventory may include stock, availability, branch/warehouse location, package/unit, provider, dispatch and retained Equipment.

Catalog is the configurable composition/BOM/recipe layer and may reference:

- Products;
- Materials;
- Services;
- Equipment when applicable;
- quantities, dosage, unit conversions and package rules;
- estimated and actual cost components;
- brand/channel/branch visibility rules.

Rules:

- Catalog does not own component lifecycle.
- Stock values come from authoritative operational sources.
- Components may have independent purchase orders, providers, currencies, lead times, taxes and accounting documents.
- Ditaly uses Catalog for recipe/dosage and franchise/internal supply composition.
- Kiseki uses Catalog for import/acquisition cost composition per sellable unit.
- PC/CG reuse Catalog to compose service/event/procedure offerings.

## 13. Sales and order concepts

Ticket is the commercial/reporting unit exposed to sales or service channels.

Examples:

- Ditaly: sold prepared item/recipe reported in sales;
- Kiseki: sold imported product or delivery item;
- PC: scheduled operative/referral whose value/status is reconciled after service confirmation;
- CG: contracted procedure/trámite.

Sales/acquisition workflows may involve Catalog, Price, inventory, agreements, orders, purchase orders, invoices, dispatch guides, transfers, commissions and fiscal configuration. No complete workflow is considered implemented outside the evidence of its responsible API and SBM-DB migrations.

## 14. Provider and branch concepts

Provider rules:

- providers are managed by authorized client users;
- provider changes preserve referential integrity;
- providers may be referenced by Products, Materials and Services;
- shared provider data does not merge domain ownership.

Branch rules:

- branch data belongs to the client business;
- branch access remains tenant-scoped;
- catalogs, prices, channels and integrations may vary by branch;
- platform provisioning remains internal.

## 15. Documentation references

Relevant documentation must use repository-relative paths under:

```text
SBM-SUITE/context/documentation/
```

Business-related documentation domains include:

- SBM Suite;
- Roadmap;
- Development;
- Technologies;
- Business modules;
- Brands and franchises;
- Security and DevSecOps;
- QA and Testing.

Specific page and subpage paths must be added when the documentation tree format is finalized.

## 16. Terminology

| Term | Meaning |
|---|---|
| Brand | Business identity operating on SBM Suite |
| Franchise | Contractual business unit provisioned by SBM |
| Tenant | Isolated operational scope for a client |
| Module | Enabled business capability |
| Client user | User operating within one authorized business scope |
| Internal SBM user | User managing platform-level operations |
| Product | Sellable business item |
| Material | Input used in production or operations |
| Service | Non-physical business offering |
| Catalog | Published grouping of offerings |
| Ticket | Operational or support request |
| Price | Monetary state and history of a priced record |
| Branch | Physical or operational location |
| Agreement | Commercial relationship and applicable conditions |

## 17. Validated business decisions

| Decision | Status | Business effect | Source |
|---|---|---|---|
| Brand operations belong to the responsible brand API | accepted | DP-API remains the reference; KS/PC/CG will own their brand-facing operations | Multi-brand architecture 2026-08-16 |
| Platform provisioning belongs to SBM-API | accepted | Tenants, franchises and contracted modules remain internal | Current architecture |
| Product, Material, Service, Catalog and Ticket remain separate domains | accepted | Independent lifecycle and ownership | Current business direction |
| Ditaly Pasta is the historical reference implementation | accepted | Preserve one year of real data and reuse validated patterns without treating DP as current production | User-confirmed 2026-08-16 |
| Git is the current source of truth for business context and documentation | accepted | Changes are versioned before future API synchronization | Current workflow |

## 18. Business constraints

- Business metrics are not yet populated from an authoritative endpoint.
- Multi-brand isolation must be enforced explicitly.
- Legacy data may contain inconsistencies.
- Service fields and relationships still require database validation.
- Contracted-module state remains platform-controlled.
- Documentation synchronization is manual in the first stage.
- Unknown operational counts remain `N/A`.

## 19. Pending business definitions

- authoritative endpoint for brand operational metrics;
- exact local, client, product, ticket and stock counts;
- definitive Service fields and relationships;
- complete sales and order workflows;
- formal module activation rules per brand;
- future brands and franchise profiles;
- automated Git-to-Notion synchronization;
- bidirectional conflict management between Git and Notion.

## 20. Multi-brand commercial baseline — 2026-08-16

### Ditaly Pasta reference

Ditaly Pasta is closed but provides real operational data and remains the reference implementation.

Example sale flow:

```text
Ticket: vaso de fetuccine al huevo / salsa bolognesa / tamaño
→ Catalog: recipe/BOM and dosage
→ Product/Material/Service components
→ inventory, purchase/transfer/sale documents, price and accounting effects
```

The Catalog may include food, packaging, condiments and logistics services. Internal stock movement may require only dispatch/transfer evidence, while sale to a franchise/client may require purchase order, invoice, dispatch guide and accounting movement. Purchase invoices may generate recoverable purchase VAT according to applicable rules.

### Kiseki Tech — sale/import now, rental later

Immediate sales scope:

```text
Ticket
→ Catalog for the imported/sold unit plus delivery
→ Product (FOB and source currency)
→ purchase-specific Service instances
→ Materials
→ Price / FX / taxes / final cost
```

Import services are instantiated per acquisition/unit even when provider/value is similar, so actual and provisioned costs remain traceable. Examples include shipping line, forwarder, customs, deconsolidation, insurance, land freight, warehouse, cranes, warranty service and warranty-replacement provision.

`sbm-util` is planned to retrieve/store authoritative exchange-rate observations (initially USD; future EUR/UF or others), while `sbm-calculation` applies deterministic financial formulas. Kiseki equipment rental, contracts, technical service and spare-parts inventory remain long-term scope and are not part of the immediate sales implementation.

### PortalConvenios.cl

PC reuses `Ticket → Catalog → Service` with scheduling and settlement semantics.

```text
SBM User → PC User → PC Client → PC Customer
```

Operational examples:

- health/wellness on-site event: Ticket starts at zero, tracks future schedule/status and is reconciled after client/customer confirmation; PC commission is configurable as a percentage of total collected;
- waiting-list referral: Ticket represents the referral/appointment and is confirmed through QR/customer interaction;
- subscription may charge the greater of a fixed monthly amount or the configured per-treated-patient amount.

`pc-client` serves PC Client users; `pc-customer` serves the downstream customer/patient with QR, profile, scheduling and confirmation.

### Consorcio y Gestión

CG reuses `Ticket → Catalog → Service → Client` for permit/procedure workflows.

Required business capabilities include:

- commercial permits, sanitary resolutions and premises enablement;
- external-provider services and calendar/stage management;
- client SII/basic business data and documentation;
- plans/drawings, missing-document dependencies and status tracking;
- `cg-client` for client-visible progress, documents, dependencies, general information and FAQ;
- SBM-MANAGER plan module with drag/drop editing, export and OCR/AI-assisted digitization from PDF/PNG through authorized services.

## 21. Pricing, package and accounting baseline

All item types use a `Package`; Service uses an explicit logical/non-physical package. Package is expected to carry quantity/unit, weight/volume when physical, packaging type and logistics classification such as frozen, disposable or technology.

Pricing target:

```text
base_net_amount
→ deterministic calculation/rules
→ net_amount
→ VAT + additional taxes/retentions
→ gross_amount
```

Price must preserve currency and exchange-rate history instead of silently overwriting converted values. Purchase/acquisition flows must distinguish estimated/provisioned versus actual cost and retain document/accounting traceability.

## 22. Channel/application audience model

| Channel | Primary audience |
|---|---|
| `sbm-manager` / `sbm-mobile` | SBM User and approved administration |
| `ks-mobile` / `pc-mobile` / `cg-mobile` | Brand/Franchise User |
| `ks-client` / `pc-client` / `cg-client` | Client User |
| `pc-customer` | PC Customer/patient |
| `ks-store` / `pc-store` / `cg-store` | Public/end-customer commercial channel |

The exact feature set is brand-owned; common naming does not imply identical business behavior.

## 23. Document boundary

This file stores business meaning, brands, franchises, capabilities, entities, rules and operational profiles.

It does not define:

- technical architecture;
- endpoint implementation details;
- container topology;
- source code structure;
- QA execution results;
- deployment procedures;
- security control implementation;
- data schema ownership;
- documentation page content.

Those concerns belong to their corresponding Suite, Project, QA, Security, Data, Deploy and Documentation contexts.
