# 🏗 Operations & Visual Planning

> Estrategia transversal de operaciones, planificación visual, diseño de espacios, documentación técnica y seguimiento de ejecución para SBM Suite.
> 
> 
> Esta página define cómo representar, planificar y controlar locales, sucursales, instalaciones, operativos, permisos, planos, tareas y recursos mediante interfaces visuales, flujos de aprobación y datos estructurados.
> 
> El objetivo no es construir un software CAD completo, sino una capa operativa visual integrada con los procesos reales de las marcas.
> 

---

# 1. Objetivo

Construir un módulo operativo capaz de:

- planificar aperturas y habilitaciones;
- representar espacios;
- administrar planos;
- ubicar elementos mediante drag-and-drop;
- organizar capas;
- registrar medidas;
- controlar versiones;
- coordinar aprobaciones;
- vincular documentos;
- hacer seguimiento de tareas;
- administrar recursos;
- relacionar operaciones con sucursales;
- integrar agentes IA;
- producir evidencia visual para el portafolio.

---

# 2. Alcance

La estrategia cubre:

- locales;
- sucursales;
- plantas;
- cocinas;
- áreas de atención;
- bodegas;
- instalaciones eléctricas;
- instalaciones sanitarias;
- equipamiento;
- mobiliario;
- permisos;
- patentes;
- resoluciones sanitarias;
- operativos;
- planos;
- capas;
- documentos;
- versiones;
- tareas;
- aprobaciones;
- inspecciones;
- incidencias;
- recursos;
- proveedores;
- cronogramas;
- agentes operativos.

---

# 3. Principios

1. **Visual-first**
    
    Los procesos espaciales deben representarse visualmente cuando aporte claridad.
    
2. **Data-backed diagrams**
    
    Los elementos visuales deben estar vinculados a datos reales.
    
3. **Not a full CAD replacement**
    
    La primera versión no intenta sustituir AutoCAD, Revit u otras herramientas profesionales.
    
4. **Versioned planning**
    
    Todo plano o diseño debe tener versiones.
    
5. **Approval workflow**
    
    Los cambios relevantes deben pasar por revisión.
    
6. **Layered representation**
    
    Electricidad, agua, equipamiento y zonas deben poder separarse por capas.
    
7. **Brand and branch awareness**
    
    Cada proyecto debe vincularse a una marca y sucursal.
    
8. **Document integration**
    
    Planos, permisos, fotografías y certificados deben estar relacionados.
    
9. **Progressive complexity**
    
    Comenzar con SVG y canvas 2D antes de agregar 3D.
    
10. **Operational traceability**
    
    Toda decisión, cambio e incidencia debe quedar registrada.
    

---

# 4. Arquitectura general

```
Operational Data
      │
      ├── Brand
      ├── Branch
      ├── Project
      ├── Floor Plan
      ├── Equipment
      ├── Documents
      └── Tasks
      │
      ▼
Visual Planning Module
      │
      ├── Canvas
      ├── Layers
      ├── Components
      ├── Measurements
      ├── Comments
      ├── Versions
      └── Approval
      │
      ▼
Operational Workflow
      │
      ├── Review
      ├── Permits
      ├── Execution
      ├── Inspection
      └── Completion
```

---

# 5. Casos de uso por marca

## Ditaly Pasta

- diseño de locales;
- distribución de cocina;
- ubicación de equipos;
- zonas de atención;
- bodegas;
- flujos de trabajo;
- permisos;
- inspecciones;
- aperturas;
- franquicias.

## Kiseki Tech

- distribución de bodega;
- almacenamiento;
- recepción de productos;
- zonas de picking;
- zonas de despacho;
- exhibición;
- seguridad.

## Consorcio Gastronómico

- levantamiento de espacios;
- planos sanitarios;
- planos eléctricos;
- distribución;
- documentación;
- expedientes;
- revisión de permisos;
- seguimiento de trámites.

## PortalConvenios.cl

- planificación de operativos;
- ubicación de módulos;
- flujo de atención;
- equipamiento;
- agenda;
- recursos;
- zonas de espera.

---

# 6. Entidades principales

| Entity | Responsibility |
| --- | --- |
| OperationalProject | Proyecto operativo |
| Site | Ubicación física |
| Branch | Sucursal |
| FloorPlan | Plano |
| Layer | Capa visual |
| VisualComponent | Elemento del plano |
| Measurement | Medida |
| Zone | Zona |
| Equipment | Equipo |
| Installation | Instalación |
| Document | Documento |
| Permit | Permiso |
| Inspection | Inspección |
| Task | Tarea |
| Issue | Incidencia |
| Approval | Aprobación |
| Version | Versión |
| Resource | Recurso |
| Supplier | Proveedor |

---

# 7. Operational Project

## Datos

- nombre;
- marca;
- empresa;
- sucursal;
- objetivo;
- tipo;
- ubicación;
- responsable;
- fecha inicio;
- fecha objetivo;
- presupuesto;
- estado;
- documentos;
- planos;
- tareas;
- riesgos.

## Estados

```
draft
planning
in_review
approved
in_execution
inspection
blocked
completed
cancelled
```

---

# 8. Visual Canvas

## Objetivo

Permitir planificación visual 2D.

## Capacidades iniciales

- drag-and-drop;
- zoom;
- pan;
- grid;
- snap;
- selección;
- rotación;
- redimensionamiento;
- agrupación;
- copiar;
- pegar;
- bloquear;
- ocultar;
- comentarios;
- exportación.

---

# 9. Component Library

## Componentes

- paredes;
- puertas;
- ventanas;
- mesas;
- equipos;
- muebles;
- lavaplatos;
- baños;
- puntos eléctricos;
- puntos de agua;
- gas;
- extintores;
- salidas;
- señalética;
- módulos;
- zonas;
- estanterías;
- racks;
- estaciones de trabajo.

## Requisitos

- tipo;
- dimensiones;
- rotación;
- categoría;
- icono;
- atributos;
- reglas;
- costo opcional;
- proveedor opcional.

---

# 10. Layers

## Capas sugeridas

- arquitectura;
- mobiliario;
- equipamiento;
- electricidad;
- agua;
- alcantarillado;
- gas;
- seguridad;
- señalética;
- evacuación;
- iluminación;
- red;
- comentarios;
- permisos.

## Funciones

- mostrar;
- ocultar;
- bloquear;
- ordenar;
- filtrar;
- exportar;
- versionar.

---

# 11. Measurements

## Capacidades

- largo;
- ancho;
- área;
- perímetro;
- distancia;
- escala;
- unidades;
- tolerancia.

## Unidades

- milímetros;
- centímetros;
- metros;
- pulgadas como opción futura.

## Regla

Las medidas visuales deben distinguir entre:

- estimadas;
- ingresadas;
- verificadas;
- certificadas.

---

# 12. Zones

## Ejemplos

- cocina;
- atención;
- espera;
- almacenamiento;
- preparación;
- despacho;
- baño;
- administración;
- circulación;
- seguridad;
- acceso restringido.

## Datos

- nombre;
- tipo;
- capacidad;
- área;
- restricciones;
- responsables;
- equipamiento;
- color visual;
- estado.

---

# 13. Equipment

## Datos

- nombre;
- tipo;
- marca;
- modelo;
- dimensiones;
- consumo;
- conexión;
- ubicación;
- proveedor;
- costo;
- fecha;
- mantenimiento;
- estado;
- documentación.

## Estados

```
planned
ordered
received
installed
active
maintenance
inactive
retired
```

---

# 14. Installations

## Tipos

- eléctrica;
- sanitaria;
- gas;
- ventilación;
- red;
- seguridad;
- climatización;
- iluminación.

## Datos

- punto;
- tipo;
- capacidad;
- especificación;
- proveedor;
- documento;
- estado;
- inspección.

---

# 15. Plans and Documents

## Tipos

- plano planta;
- plano eléctrico;
- plano sanitario;
- plano de gas;
- plano de evacuación;
- permiso;
- patente;
- resolución;
- certificado;
- fotografía;
- informe;
- contrato;
- presupuesto.

## Requisitos

- versión;
- fecha;
- autor;
- estado;
- archivo;
- comentarios;
- aprobación;
- relación con proyecto.

---

# 16. Versioning

## Objetivo

Mantener historial de cambios.

## Datos

- número;
- fecha;
- autor;
- cambio;
- motivo;
- archivo;
- snapshot;
- estado;
- aprobación.

## Estados

```
draft
review
approved
superseded
archived
```

---

# 17. Comparison

## Futuro

Permitir comparar versiones:

- elementos agregados;
- elementos eliminados;
- elementos movidos;
- cambios de medida;
- cambios de capa;
- comentarios;
- costo.

---

# 18. Approval Workflow

## Flujo

```
Draft
  ↓
Technical Review
  ↓
Operational Review
  ↓
Compliance Review
  ↓
Approval
  ↓
Execution
```

## Roles

- diseñador;
- técnico;
- operaciones;
- administrador;
- legal;
- cliente;
- inspector.

---

# 19. Tasks

## Datos

- título;
- descripción;
- proyecto;
- responsable;
- fecha;
- prioridad;
- estado;
- dependencia;
- evidencia;
- plano asociado;
- ubicación;
- costo;
- proveedor.

## Estados

```
backlog
ready
in_progress
blocked
review
completed
cancelled
```

---

# 20. Kanban

## Vistas

- por proyecto;
- por responsable;
- por sucursal;
- por prioridad;
- por etapa;
- por permiso;
- por proveedor.

## Integración

- Azure Boards para tareas técnicas;
- Jira para tareas operativas;
- módulo SBM para seguimiento funcional.

---

# 21. Timeline

## Capacidades

- hitos;
- dependencias;
- fechas;
- ruta crítica futura;
- responsables;
- avances;
- retrasos;
- bloqueos.

## Herramientas

- timeline interno;
- Gantt como etapa futura;
- integración con calendarios.

---

# 22. Inspections

## Tipos

- interna;
- sanitaria;
- eléctrica;
- seguridad;
- municipal;
- recepción;
- calidad;
- franquicia.

## Datos

- fecha;
- inspector;
- checklist;
- resultado;
- hallazgos;
- evidencia;
- acciones;
- plazo;
- estado.

---

# 23. Checklists

## Casos

- apertura;
- instalación;
- seguridad;
- limpieza;
- permisos;
- recepción;
- inspección;
- cierre;
- mantenimiento.

## Funciones

- plantillas;
- campos obligatorios;
- fotografías;
- firma;
- comentarios;
- estado;
- evidencia.

---

# 24. Issues

## Tipos

- diseño;
- ejecución;
- seguridad;
- permiso;
- proveedor;
- costo;
- plazo;
- calidad.

## Severidad

- blocker;
- critical;
- major;
- minor;
- observation.

## Flujo

```
Detected
  ↓
Assigned
  ↓
Action
  ↓
Verification
  ↓
Closed
```

---

# 25. Resources

## Tipos

- personas;
- equipos;
- vehículos;
- herramientas;
- salas;
- módulos;
- insumos;
- proveedores.

## Datos

- disponibilidad;
- capacidad;
- ubicación;
- costo;
- responsable;
- estado;
- reserva.

---

# 26. Scheduling

## Casos

- instalación;
- inspección;
- operativo;
- visita;
- mantenimiento;
- recepción;
- entrega;
- capacitación.

## Integración

- Google Calendar;
- Microsoft Calendar;
- agentes;
- n8n;
- notificaciones.

---

# 27. Budget Control

## Datos

- presupuesto inicial;
- comprometido;
- ejecutado;
- variación;
- proveedor;
- categoría;
- centro de costo;
- proyecto.

## Integración

- Finance Module;
- cuentas por pagar;
- compras;
- órdenes;
- facturas.

---

# 28. Supplier Management

## Casos

- cotización;
- orden;
- instalación;
- inspección;
- evidencia;
- pago;
- evaluación;
- garantía.

## Datos

- proveedor;
- contacto;
- servicio;
- plazo;
- costo;
- documentos;
- evaluación;
- incidencias.

---

# 29. Permits and Compliance

## Casos

- patente comercial;
- resolución sanitaria;
- permiso municipal;
- certificado eléctrico;
- gas;
- recepción;
- autorización;
- contrato.

## Datos

- tipo;
- organismo;
- fecha solicitud;
- vencimiento;
- estado;
- documentos;
- observaciones;
- responsable.

---

# 30. Permit Workflow

```
Requirements
    ↓
Document Collection
    ↓
Submission
    ↓
Observation
    ↓
Correction
    ↓
Approval
    ↓
Renewal
```

---

# 31. Map and Location

## Casos

- ubicación;
- acceso;
- zonas;
- cobertura;
- operativos;
- rutas;
- sucursales.

## Tecnologías

- Google Maps;
- OpenStreetMap;
- geocoding;
- geofencing futuro.

---

# 32. Floor Plan Import

## Formatos iniciales

- PNG;
- JPG;
- PDF;
- SVG.

## Formatos futuros

- DXF;
- DWG mediante conversión;
- IFC como investigación.

## Estrategia

1. importar archivo;
2. calibrar escala;
3. bloquear fondo;
4. agregar elementos;
5. crear capas;
6. guardar versión.

---

# 33. Export

## Formatos

- PNG;
- PDF;
- SVG;
- JSON;
- reporte técnico;
- listado de elementos;
- presupuesto;
- checklist.

---

# 34. 3D Visualization

## Estado

- Planned;
- posterior al editor 2D.

## Tecnologías

- Three.js;
- Blender;
- modelos glTF;
- WebGL.

## Casos

- recorrido;
- distribución;
- presentación;
- validación;
- render comercial.

---

# 35. Technologies

## Frontend options

| Technology | Use |
| --- | --- |
| Vue Flow | Flujos y nodos |
| React Flow | Flujos y diagramas |
| Konva.js | Canvas 2D |
| Fabric.js | Editor visual |
| SVG | Planos y exportación |
| Three.js | Visualización 3D |

## Recomendación

Para el editor de planos:

- Konva.js o Fabric.js para canvas 2D;
- SVG para exportación y elementos vectoriales;
- React Flow o Vue Flow para procesos, no como motor CAD principal;
- Three.js solo en una fase posterior.

---

# 36. Frontend Architecture

## Módulos

- canvas;
- toolbar;
- component library;
- properties panel;
- layers panel;
- history;
- comments;
- versions;
- export;
- approvals.

---

# 37. Backend Architecture

## Responsabilidades

- proyectos;
- planos;
- componentes;
- capas;
- versiones;
- permisos;
- tareas;
- documentos;
- auditoría;
- exportaciones;
- integraciones.

## Almacenamiento

- PostgreSQL para metadata;
- object storage para archivos;
- Cloudinary para multimedia pública;
- NAS para respaldo;
- JSON o estructura vectorial para canvas.

---

# 38. Data Model for Canvas

## Estructura conceptual

```json
{
  "plan_id": "uuid",
  "version": 3,
  "scale": 100,
  "unit": "cm",
  "layers": [],
  "components": [],
  "measurements": [],
  "comments": []
}
```

## Requisitos

- validación;
- versionado;
- migración de schema;
- historial;
- bloqueo;
- auditoría.

---

# 39. Collaboration

## Capacidades futuras

- comentarios;
- menciones;
- revisión;
- presencia;
- bloqueo de edición;
- edición colaborativa;
- historial.

## Implementación progresiva

Primero:

- edición individual;
- comentarios;
- versiones.

Después:

- colaboración en tiempo real;
- WebSockets;
- conflictos;
- presencia.

---

# 40. Operations Agent

## Responsabilidades futuras

- resumir estado;
- detectar bloqueos;
- generar checklist;
- crear tareas;
- preparar reportes;
- revisar vencimientos;
- coordinar responsables;
- analizar incidencias.

## Límites

- no aprobar permisos;
- no modificar planos sin confirmación;
- no cerrar inspecciones críticas;
- no cambiar presupuesto.

---

# 41. Compliance Agent

## Responsabilidades futuras

- revisar documentación;
- identificar faltantes;
- resumir observaciones;
- controlar vencimientos;
- generar checklist;
- preparar expedientes.

## Límites

- no reemplazar revisión profesional;
- no declarar cumplimiento definitivo;
- no presentar documentos sin aprobación.

---

# 42. Visual Planning Agent

## Responsabilidades futuras

- proponer distribución;
- detectar colisiones;
- validar medidas básicas;
- sugerir componentes;
- generar alternativas;
- explicar cambios.

## Regla

Las propuestas deben considerarse borradores hasta revisión humana.

---

# 43. AI and Computer Vision

## Casos

- OCR;
- extracción de medidas;
- lectura de etiquetas;
- clasificación de planos;
- detección de elementos;
- comparación visual;
- generación de reportes;
- análisis de fotografías.

## Estado

- Research;
- posterior a datos y editor base.

---

# 44. Automation

## Casos

- recordatorios;
- vencimientos;
- creación de tareas;
- actualización de estado;
- aprobación;
- generación de reportes;
- alertas;
- sincronización documental.

## Herramientas

- Celery;
- Celery Beat;
- Kafka;
- n8n;
- agentes;
- webhooks.

---

# 45. Operational Events

```
project.created
plan.versioned
plan.approved
task.blocked
inspection.completed
issue.created
permit.submitted
permit.approved
equipment.installed
project.completed
```

---

# 46. Integration with Finance

## Casos

- presupuesto;
- costos;
- órdenes;
- facturas;
- pagos;
- desviaciones;
- proveedores;
- activos.

---

# 47. Integration with Inventory

## Casos

- equipamiento;
- herramientas;
- insumos;
- movimientos;
- reservas;
- consumo;
- pérdidas;
- instalación.

---

# 48. Integration with Commerce

## Casos

- habilitación de tienda;
- apertura de sucursal;
- equipamiento comercial;
- señalética;
- puntos de retiro;
- layout de exhibición.

---

# 49. Security

## Controles

- permisos;
- marca;
- sucursal;
- proyecto;
- documentos privados;
- acceso por rol;
- logs;
- versiones;
- aprobación;
- cifrado;
- backups.

---

# 50. QA

## Pruebas

- canvas;
- drag-and-drop;
- zoom;
- escala;
- capas;
- versiones;
- permisos;
- export;
- documentos;
- aprobaciones;
- tareas;
- auditoría;
- performance.

## E2E

```
Create Project
   ↓
Import Plan
   ↓
Add Components
   ↓
Save Version
   ↓
Review
   ↓
Approve
   ↓
Generate Report
```

---

# 51. Performance

## Riesgos

- planos grandes;
- muchos elementos;
- imágenes pesadas;
- historial;
- colaboración;
- exportación.

## Controles

- virtualización;
- lazy loading;
- simplificación;
- compresión;
- snapshots;
- workers;
- procesamiento asíncrono.

---

# 52. Observability

## Métricas

- proyectos activos;
- tareas bloqueadas;
- inspecciones;
- vencimientos;
- cambios de plano;
- errores;
- exportaciones;
- tiempo de aprobación;
- retrasos;
- presupuesto.

---

# 53. Roadmap de implementación

## Etapa 1 — Modelo operativo

1. proyectos;
2. sucursales;
3. tareas;
4. documentos;
5. permisos;
6. estados;
7. auditoría.

## Etapa 2 — Editor 2D

1. canvas;
2. importación;
3. escala;
4. componentes;
5. capas;
6. medidas;
7. guardado.

## Etapa 3 — Versiones y aprobaciones

1. versiones;
2. comentarios;
3. revisión;
4. aprobación;
5. exportación;
6. reportes.

## Etapa 4 — Operación

1. checklists;
2. inspecciones;
3. incidencias;
4. recursos;
5. proveedores;
6. presupuesto.

## Etapa 5 — Inteligencia

1. Operations Agent;
2. Compliance Agent;
3. Visual Planning Agent;
4. OCR;
5. computer vision;
6. 3D.

---

# 54. Prioridad actual

## Urgente

1. definir modelo de proyectos;
2. definir permisos y documentos;
3. definir relación con sucursales;
4. definir tareas y estados;
5. definir casos Ditaly Pasta y Consorcio Gastronómico.

## Corto plazo

1. prototipo canvas;
2. importación de plano;
3. capas;
4. componentes;
5. medidas;
6. versiones.

## Mediano plazo

1. aprobaciones;
2. inspecciones;
3. checklists;
4. proveedores;
5. presupuesto;
6. agentes.

## Largo plazo

1. colaboración en tiempo real;
2. 3D;
3. computer vision;
4. análisis automático;
5. simulación;
6. optimización de layouts.

---

# 55. Evidencia para portafolio

## Entregables

- editor drag-and-drop;
- plano versionado;
- capas;
- medidas;
- workflow de aprobación;
- checklist;
- inspección;
- dashboard operativo;
- integración con tareas;
- exportación PDF;
- demo 3D futura;
- video técnico.

---

# 56. Criterio de finalización

Una capacidad operativa se considera implementada cuando:

1. está vinculada a un proyecto;
2. tiene marca y sucursal;
3. tiene permisos;
4. tiene versiones;
5. tiene trazabilidad;
6. tiene aprobación cuando corresponde;
7. tiene pruebas;
8. tiene documentación;
9. tiene observabilidad;
10. puede demostrarse.

---

# 57. Visión final

```
Operational Projects
        +
Visual Planning
        +
Documents and Permits
        +
Tasks and Inspections
        +
Approvals
        +
AI Assistance
```

SBM Suite debe evolucionar hacia una plataforma operativa visual capaz de planificar, documentar, ejecutar y auditar proyectos físicos y administrativos desde una misma arquitectura multimarcas.

---

# 58. CG plans/documents workflow — 2026-08-16

CG requires staged procedure workflows, missing-document dependencies, provider calendars and plan/document handling. Planned SBM-MANAGER capability includes drag-and-drop plan editing/export plus OCR/AI-assisted digitization from PDF/PNG through authorized AI/tool services. `cg-client` exposes only client-scoped progress, documentation, dependencies and FAQ.
