# 💰 Finance, Accounting & Tax Integration

> Estrategia transversal de finanzas, contabilidad e integración tributaria para SBM Suite.
> 
> 
> Esta página define cómo centralizar flujo de caja, cuentas por cobrar, cuentas por pagar, presupuestos, conciliaciones, documentos tributarios, rentabilidad y proyecciones, manteniendo una arquitectura desacoplada respecto del SII y de proveedores externos.
> 
> El objetivo es construir una capa financiera confiable, auditable y automatizable, sin convertir SBM Suite en un sistema contable rígidamente acoplado a cambios regulatorios.
> 

---

# 1. Objetivo

Construir una plataforma financiera y contable capaz de:

- registrar ingresos y egresos;
- administrar cuentas por cobrar;
- administrar cuentas por pagar;
- proyectar flujo de caja;
- controlar presupuestos;
- medir rentabilidad;
- conciliar pagos;
- integrar facturación electrónica;
- registrar documentos tributarios;
- controlar centros de costo;
- analizar resultados por marca;
- detectar desviaciones;
- automatizar tareas;
- integrar agentes IA;
- mantener trazabilidad completa.

---

# 2. Alcance

La estrategia cubre:

- flujo de caja;
- ingresos;
- egresos;
- cuentas por cobrar;
- cuentas por pagar;
- presupuestos;
- centros de costo;
- conciliación bancaria;
- conciliación de pagos;
- ventas;
- compras;
- facturas;
- boletas;
- notas de crédito;
- notas de débito;
- guías de despacho;
- proveedores DTE;
- SII;
- impuestos;
- tipo de cambio;
- proyecciones;
- rentabilidad;
- alertas;
- auditoría;
- agentes financieros y contables.

---

# 3. Principios

1. **Auditability first**
    
    Toda operación financiera debe dejar trazabilidad.
    
2. **Separation of concerns**
    
    Finanzas, contabilidad y tributación deben estar separadas pero integradas.
    
3. **External tax provider adapter**
    
    SBM Suite no debe depender directamente de la implementación técnica del SII.
    
4. **Human approval**
    
    Pagos, emisión de documentos y cambios críticos requieren aprobación.
    
5. **Single source of truth**
    
    Los movimientos financieros deben tener una fuente oficial.
    
6. **Reconciliation**
    
    Toda operación relevante debe poder conciliarse.
    
7. **Immutable history**
    
    Los movimientos aprobados no deben sobrescribirse sin trazabilidad.
    
8. **Brand-aware**
    
    Toda operación debe identificar marca, empresa y centro de costo.
    
9. **Automation with control**
    
    Automatizar sin eliminar supervisión.
    
10. **Progressive implementation**
    
    Comenzar por flujo, cuentas y conciliación antes de contabilidad avanzada.
    

---

# 4. Arquitectura general

```
Operational Systems
       │
       ├── Sales
       ├── Orders
       ├── Purchases
       ├── Inventory
       ├── Payments
       └── Payroll Future
       │
       ▼
Finance Layer
       │
       ├── Cash Flow
       ├── Accounts Receivable
       ├── Accounts Payable
       ├── Budgets
       ├── Cost Centers
       └── Reconciliation
       │
       ▼
Accounting Layer
       │
       ├── Journals
       ├── Documents
       ├── Taxes
       ├── Ledger
       └── Reports
       │
       ▼
Tax Integration Layer
       │
       └── DTE Provider Adapter
               │
               ▼
        External Provider
               │
               ▼
              SII
```

---

# 5. Separación de dominios

## Finanzas

Responsable de:

- flujo de caja;
- liquidez;
- pagos;
- cobros;
- presupuestos;
- proyecciones;
- rentabilidad;
- conciliación.

## Contabilidad

Responsable de:

- asientos;
- cuentas;
- libros;
- períodos;
- documentos;
- saldos;
- informes;
- cierres.

## Tributación

Responsable de:

- DTE;
- estados ante proveedor;
- aceptación;
- rechazo;
- acuses;
- impuestos;
- integración con SII.

---

# 6. Entidades principales

| Entity | Responsibility |
| --- | --- |
| FinancialAccount | Cuenta financiera |
| BankAccount | Cuenta bancaria |
| CashRegister | Caja |
| Income | Ingreso |
| Expense | Egreso |
| Receivable | Cuenta por cobrar |
| Payable | Cuenta por pagar |
| Payment | Pago |
| Collection | Cobro |
| Budget | Presupuesto |
| CostCenter | Centro de costo |
| Reconciliation | Conciliación |
| AccountingAccount | Cuenta contable |
| JournalEntry | Asiento |
| TaxDocument | Documento tributario |
| TaxProvider | Proveedor DTE |
| ExchangeRate | Tipo de cambio |
| FinancialPeriod | Período |
| FinancialProjection | Proyección |

---

# 7. Modelo por marca y empresa

Cada movimiento debe identificar:

- marca;
- empresa legal;
- sucursal;
- centro de costo;
- unidad de negocio;
- moneda;
- fecha;
- origen;
- responsable;
- estado;
- documento asociado.

## Regla

La marca comercial y la entidad legal no siempre son lo mismo y deben modelarse separadamente.

---

# 8. Flujo de caja

## Objetivo

Conocer entradas, salidas y saldo esperado.

## Componentes

- saldo inicial;
- ingresos;
- egresos;
- compromisos;
- cuentas por cobrar;
- cuentas por pagar;
- proyección;
- saldo final;
- escenario.

## Vistas

- diaria;
- semanal;
- mensual;
- por marca;
- por empresa;
- por sucursal;
- por centro de costo.

---

# 9. Tipos de flujo

| Type | Example |
| --- | --- |
| Operating | Ventas, proveedores, gastos |
| Investing | Equipamiento, infraestructura |
| Financing | Créditos, aportes, deuda |
| Tax | IVA, pagos tributarios |
| Intercompany | Transferencias entre entidades |

---

# 10. Ingresos

## Fuentes

- ventas;
- servicios;
- convenios;
- franquicias;
- comisiones;
- marketplace;
- reembolsos;
- otros ingresos.

## Datos

- monto;
- moneda;
- fecha;
- cliente;
- canal;
- documento;
- estado;
- cuenta;
- centro de costo;
- marca.

---

# 11. Egresos

## Tipos

- compras;
- proveedores;
- arriendos;
- sueldos;
- servicios;
- marketing;
- impuestos;
- infraestructura;
- comisiones;
- transporte;
- mantención.

## Controles

- categoría;
- centro de costo;
- aprobación;
- documento;
- proveedor;
- método;
- conciliación;
- evidencia.

---

# 12. Cuentas por cobrar

## Estados

```
draft
issued
pending
partially_paid
paid
overdue
cancelled
written_off
```

## Datos

- cliente;
- documento;
- monto;
- vencimiento;
- pagos;
- saldo;
- mora;
- responsable;
- origen;
- marca.

## Automatización

- recordatorios;
- alertas;
- seguimiento;
- clasificación;
- proyección;
- escalamiento.

---

# 13. Cuentas por pagar

## Estados

```
draft
approved
scheduled
partially_paid
paid
overdue
cancelled
```

## Datos

- proveedor;
- documento;
- monto;
- vencimiento;
- cuenta;
- centro de costo;
- aprobación;
- pago;
- saldo;
- marca.

---

# 14. Presupuestos

## Niveles

- empresa;
- marca;
- sucursal;
- departamento;
- proyecto;
- campaña;
- centro de costo.

## Datos

- período;
- monto;
- ejecutado;
- comprometido;
- disponible;
- desviación;
- responsable;
- estado.

---

# 15. Centros de costo

## Objetivo

Relacionar gastos e ingresos con unidades de responsabilidad.

## Ejemplos

- administración;
- marketing;
- tecnología;
- local;
- sucursal;
- campaña;
- proyecto;
- operaciones;
- franquicia.

---

# 16. Rentabilidad

## Dimensiones

- marca;
- producto;
- servicio;
- canal;
- sucursal;
- cliente;
- campaña;
- marketplace;
- período.

## Indicadores

- ingresos;
- costo;
- margen bruto;
- gastos;
- margen operacional;
- contribución;
- rentabilidad;
- EBITDA futuro.

---

# 17. Costeo

## Tipos

- costo directo;
- costo indirecto;
- costo estándar;
- costo promedio;
- costo importación;
- costo por receta;
- costo por servicio;
- costo por proyecto.

## Caso Kiseki Tech

```
Purchase USD
   +
Exchange Rate
   +
Transport
   +
Tariffs
   +
VAT
   +
Marketplace Fees
   +
Operational Cost
   =
Total Landed Cost
```

---

# 18. Tipo de cambio

## Fuente

Banco Central de Chile u otra fuente oficial autorizada.

## Datos

- moneda;
- valor;
- fecha;
- fuente;
- timestamp;
- estado;
- validación.

## Casos

- importaciones;
- valorización;
- precios;
- proyecciones;
- conciliación;
- reportes.

---

# 19. Conciliación bancaria

## Objetivo

Relacionar movimientos bancarios con operaciones de SBM Suite.

## Flujo

```
Bank Movement
      ↓
Import or API
      ↓
Matching Rules
      ↓
Suggested Match
      ↓
Human Review
      ↓
Reconciled
```

## Criterios

- monto;
- fecha;
- referencia;
- cliente;
- proveedor;
- documento;
- método;
- cuenta.

---

# 20. Conciliación de pagos

## Fuentes

- Mercado Pago;
- Webpay;
- Stripe;
- transferencias;
- marketplace;
- efectivo;
- POS.

## Requisitos

- transaction ID;
- external ID;
- amount;
- fees;
- taxes;
- settlement;
- status;
- order;
- reconciliation date.

---

# 21. Pagos

## Estados

```
created
pending
authorized
paid
failed
reversed
refunded
cancelled
```

## Controles

- idempotencia;
- webhooks;
- conciliación;
- auditoría;
- evidencia;
- autorización;
- aprobación cuando corresponda.

---

# 22. Contabilidad

## Objetivo

Registrar hechos económicos de forma estructurada.

## Componentes

- plan de cuentas;
- asientos;
- períodos;
- saldos;
- libros;
- documentos;
- centros de costo;
- reportes;
- cierre.

---

# 23. Plan de cuentas

## Estructura

- activos;
- pasivos;
- patrimonio;
- ingresos;
- costos;
- gastos;
- impuestos;
- cuentas de orden.

## Requisitos

- código;
- nombre;
- tipo;
- nivel;
- padre;
- moneda;
- estado;
- empresa;
- vigencia.

---

# 24. Asientos contables

## Datos

- fecha;
- período;
- descripción;
- origen;
- documento;
- cuenta;
- débito;
- crédito;
- centro de costo;
- marca;
- estado;
- usuario.

## Regla

Debe cumplirse:

```
Total Debit = Total Credit
```

---

# 25. Estados contables

## Estados

```
draft
validated
approved
posted
reversed
```

## Reglas

- no editar asientos contabilizados;
- corregir mediante reversa;
- mantener historial;
- registrar aprobación;
- bloquear períodos cerrados.

---

# 26. Períodos contables

## Estados

- open;
- review;
- closed;
- locked.

## Controles

- fechas;
- cierre;
- reapertura autorizada;
- auditoría;
- reportes;
- conciliación previa.

---

# 27. Documentos tributarios

## Tipos

- factura electrónica;
- factura exenta;
- boleta electrónica;
- nota de crédito;
- nota de débito;
- guía de despacho;
- factura de compra;
- otros DTE aplicables.

## Datos

- tipo;
- folio;
- emisor;
- receptor;
- monto;
- impuestos;
- fecha;
- estado;
- XML;
- PDF;
- proveedor;
- tracking;
- respuesta.

---

# 28. Arquitectura DTE

```
SBM Suite
    ↓
Billing and Tax Module
    ↓
DTE Provider Adapter
    ↓
External Billing Provider
    ↓
SII
```

## Responsabilidad de SBM Suite

- preparar datos;
- validar;
- solicitar emisión;
- almacenar resultado;
- consultar estado;
- gestionar errores;
- asociar documento;
- auditar.

## Responsabilidad del proveedor

- firma;
- folios;
- XML;
- transmisión;
- cambios técnicos SII;
- respuestas;
- cumplimiento específico.

---

# 29. DTE Provider Adapter

## Objetivo

Evitar acoplamiento a un proveedor.

## Interfaz conceptual

```
issue_document()
cancel_document()
get_document_status()
download_xml()
download_pdf()
send_to_customer()
get_rejections()
get_acknowledgements()
```

## Requisitos

- versión;
- provider ID;
- credentials;
- timeout;
- retries;
- mapping;
- idempotencia;
- logs.

---

# 30. Selección de proveedor DTE

## Criterios

- API disponible;
- documentación;
- cobertura DTE;
- soporte;
- SLA;
- precio;
- sandbox;
- webhooks;
- portabilidad;
- seguridad;
- estabilidad.

## Nota

No se debe elegir ni documentar un proveedor específico hasta verificar su oferta vigente.

---

# 31. Estados DTE

```
draft
pending
submitted
accepted
accepted_with_observations
rejected
cancelled
credited
```

## Requisitos

- historial;
- mensajes;
- código externo;
- retries;
- alertas;
- auditoría.

---

# 32. Notas de crédito y débito

## Casos

- devolución;
- diferencia;
- anulación;
- descuento posterior;
- corrección;
- recargo.

## Requisitos

- documento de referencia;
- motivo;
- monto;
- aprobación;
- trazabilidad;
- conciliación.

---

# 33. Guías de despacho

## Casos

- traslado;
- entrega;
- despacho;
- retiro;
- movimiento de inventario.

## Integración

- pedido;
- bodega;
- transporte;
- cliente;
- estado;
- DTE provider.

---

# 34. IVA e impuestos

## Alcance

- IVA débito;
- IVA crédito;
- exentos;
- retenciones;
- otros impuestos;
- períodos;
- conciliación.

## Principio

Las reglas tributarias deben mantenerse configurables y validadas por profesionales competentes.

---

# 35. Auditoría financiera

## Eventos

- creación;
- aprobación;
- modificación;
- reversa;
- pago;
- conciliación;
- emisión;
- rechazo;
- cierre;
- reapertura.

## Datos

- actor;
- fecha;
- acción;
- entidad;
- valor anterior;
- valor nuevo;
- motivo;
- IP;
- trace ID.

---

# 36. Approval Workflow

## Operaciones que requieren aprobación

- pagos;
- devolución;
- anulación;
- cambio de precio;
- emisión extraordinaria;
- presupuesto;
- ajuste de inventario con impacto financiero;
- reapertura de período;
- write-off;
- modificación de datos tributarios.

---

# 37. Segregation of Duties

## Objetivo

Evitar que una sola persona controle todo el proceso.

## Separaciones

- quien crea no aprueba;
- quien aprueba no concilia;
- quien paga no modifica cuenta;
- quien emite no anula sin autorización;
- agentes IA no aprueban operaciones críticas.

---

# 38. Finance Agent

## Responsabilidades futuras

- resumir flujo;
- detectar vencimientos;
- generar alertas;
- proyectar caja;
- identificar desviaciones;
- preparar reportes;
- sugerir acciones;
- consultar cuentas;
- explicar indicadores.

## Límites

- no ejecutar pagos;
- no modificar presupuestos;
- no emitir documentos críticos;
- no aprobar operaciones.

---

# 39. Accounting Agent

## Responsabilidades futuras

- clasificar documentos;
- sugerir cuentas;
- detectar inconsistencias;
- preparar borradores;
- conciliar;
- resumir períodos;
- revisar saldos;
- generar checklists.

## Límites

- no contabilizar de forma irreversible sin aprobación;
- no cerrar períodos;
- no presentar declaraciones;
- no reemplazar revisión profesional.

---

# 40. Tax Integration Agent

## Responsabilidades futuras

- consultar estados;
- detectar rechazos;
- resumir errores;
- preparar reintentos;
- identificar documentos faltantes;
- generar alertas.

## Límites

- no alterar datos tributarios sin autorización;
- no interpretar legislación como fuente definitiva;
- no emitir automáticamente operaciones sensibles.

---

# 41. Automation

## Casos

- recordatorios;
- vencimientos;
- conciliación sugerida;
- importación bancaria;
- tipo de cambio;
- emisión DTE;
- seguimiento;
- reportes;
- alertas;
- clasificación documental.

## Herramientas

- Celery;
- Celery Beat;
- Kafka;
- n8n;
- agentes;
- webhooks.

---

# 42. Eventos financieros

```
invoice.issued
invoice.accepted
invoice.rejected
payment.received
payment.failed
expense.approved
payable.overdue
receivable.overdue
budget.exceeded
bank.reconciled
period.closed
exchange_rate.updated
```

---

# 43. Integración con comercio

## Datos compartidos

- pedido;
- venta;
- pago;
- devolución;
- cliente;
- documento;
- comisión;
- impuesto;
- canal.

## Flujo

```
Order
  ↓
Payment
  ↓
Invoice or Receipt
  ↓
Revenue
  ↓
Reconciliation
  ↓
Accounting
```

---

# 44. Integración con inventario

## Impactos

- costo de venta;
- valorización;
- ajustes;
- pérdidas;
- mermas;
- transferencias;
- compras;
- stock.

---

# 45. Integración con marketplaces

## Datos

- ventas;
- comisiones;
- retenciones;
- despacho;
- pago;
- devolución;
- liquidación.

## Requisito

Conciliar liquidaciones externas con pedidos internos.

---

# 46. Reporting

## Reportes financieros

- flujo de caja;
- cuentas por cobrar;
- cuentas por pagar;
- presupuesto;
- rentabilidad;
- ventas;
- gastos;
- conciliación;
- proyección.

## Reportes contables

- balance;
- estado de resultados;
- mayor;
- diario;
- saldos;
- centros de costo;
- documentos.

## Reportes tributarios

- DTE emitidos;
- aceptados;
- rechazados;
- notas;
- IVA;
- documentos pendientes.

---

# 47. Dashboards

## Ejecutivo

- cash position;
- ingresos;
- egresos;
- cuentas vencidas;
- margen;
- presupuesto;
- proyección.

## Financiero

- flujo;
- bancos;
- pagos;
- cobros;
- conciliaciones;
- desviaciones.

## Contable

- asientos;
- períodos;
- saldos;
- documentos;
- errores.

## Tributario

- estados DTE;
- rechazos;
- folios;
- documentos pendientes.

---

# 48. Forecasting

## Casos

- cash flow;
- ventas;
- gastos;
- cobranza;
- pagos;
- demanda;
- rentabilidad.

## Enfoque

1. baseline;
2. modelo clásico;
3. evaluación;
4. aprobación;
5. monitoreo.

---

# 49. Anomaly Detection

## Casos

- gasto atípico;
- pago duplicado;
- precio fuera de rango;
- comisión inesperada;
- documento duplicado;
- diferencia bancaria;
- movimiento no conciliado;
- fraude potencial.

---

# 50. Security

## Controles

- cifrado;
- permisos;
- segregación;
- MFA;
- logs;
- auditoría;
- secretos;
- no exponer datos bancarios;
- backups;
- acceso por marca;
- aprobación.

---

# 51. Privacy

## Datos sensibles

- cuentas;
- pagos;
- RUT;
- documentos;
- saldos;
- proveedores;
- clientes;
- información tributaria.

## Reglas

- minimización;
- acceso restringido;
- retención;
- cifrado;
- enmascaramiento;
- auditoría.

---

# 52. QA

## Pruebas

- cálculos;
- redondeos;
- monedas;
- impuestos;
- asientos;
- balance;
- conciliación;
- idempotencia;
- webhooks;
- documentos;
- permisos;
- períodos;
- aprobaciones;
- reversas.

## Cobertura recomendada

- lógica financiera: 90% o más;
- permisos: 90% o más;
- DTE adapter: contratos completos;
- conciliación: escenarios críticos.

---

# 53. Observability

## Métricas

- pagos procesados;
- fallas;
- conciliaciones;
- cuentas vencidas;
- documentos rechazados;
- latencia proveedor;
- retries;
- diferencias;
- presupuesto excedido;
- cash position.

---

# 54. Roadmap de implementación

## Etapa 1 — Base financiera

1. cuentas;
2. ingresos;
3. egresos;
4. centros de costo;
5. flujo de caja;
6. presupuestos;
7. reportes.

## Etapa 2 — Cobros y pagos

1. cuentas por cobrar;
2. cuentas por pagar;
3. vencimientos;
4. pagos;
5. cobranza;
6. conciliación.

## Etapa 3 — Documentos

1. modelo DTE;
2. adapter;
3. sandbox;
4. estados;
5. webhooks;
6. PDF y XML;
7. errores.

## Etapa 4 — Contabilidad

1. plan de cuentas;
2. asientos;
3. períodos;
4. cierres;
5. reportes;
6. reversas.

## Etapa 5 — Inteligencia

1. forecasting;
2. anomalías;
3. Finance Agent;
4. Accounting Agent;
5. Tax Integration Agent;
6. dashboards avanzados.

---

# 55. Prioridad actual

## Urgente

1. definir empresas legales y marcas;
2. definir centros de costo;
3. definir modelo financiero;
4. definir pagos y conciliación;
5. diseñar adapter DTE;
6. verificar proveedores vigentes;
7. documentar controles.

## Corto plazo

1. flujo de caja;
2. cuentas por cobrar;
3. cuentas por pagar;
4. presupuestos;
5. conciliación;
6. reportes.

## Mediano plazo

1. integración DTE;
2. documentos;
3. contabilidad;
4. dashboards;
5. agentes;
6. forecasting.

## Largo plazo

1. cierres avanzados;
2. multiempresa;
3. consolidación;
4. automatización contable;
5. analítica financiera;
6. inteligencia predictiva.

---

# 56. Evidencia para portafolio

## Entregables

- dashboard financiero;
- flujo de caja;
- conciliación;
- adapter DTE;
- contratos;
- workflow de aprobación;
- pruebas de cálculo;
- auditoría;
- forecasting;
- agente financiero;
- demo de emisión sandbox.

---

# 57. Criterio de finalización

Una capacidad financiera se considera implementada cuando:

1. tiene fuente oficial;
2. tiene trazabilidad;
3. tiene permisos;
4. tiene aprobación;
5. tiene conciliación;
6. tiene pruebas;
7. tiene seguridad;
8. tiene documentación;
9. tiene observabilidad;
10. puede auditarse;
11. puede revertirse cuando corresponde;
12. puede demostrarse.

---

# 58. Visión final

```
Operational Data
      +
Financial Control
      +
Accounting Records
      +
Tax Integration
      +
Automation
      +
AI Assistance
      +
Human Approval
```

SBM Suite debe evolucionar hacia una plataforma financiera y contable multimarcas capaz de controlar, conciliar, proyectar y auditar operaciones, manteniendo la integración tributaria desacoplada y supervisada.

---

# 59. sbm-calculation and commercial costing baseline — 2026-08-16

`sbm-calculation` is the planned shared engine for `base_net_amount → net_amount → taxes → gross_amount`, currencies/FX, commissions, provisions, cost allocation and reconciliation. KS requires acquisition-specific import costs and provision-versus-actual tracking; PC requires percentage commissions and monthly max(fixed fee, per-treated-patient amount); Ditaly provides real historical purchase/sale/VAT/document flows.
