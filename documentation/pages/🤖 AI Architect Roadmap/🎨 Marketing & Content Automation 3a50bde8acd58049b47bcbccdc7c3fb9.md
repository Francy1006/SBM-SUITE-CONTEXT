# 🎨 Marketing & Content Automation

> Estrategia transversal de marketing, producción de contenido y automatización creativa para SBM Suite.
> 
> 
> Esta página define cómo planificar, producir, revisar, publicar y medir contenido para múltiples marcas utilizando agentes IA, herramientas creativas, automatización, APIs oficiales y aprobación humana.
> 
> El objetivo es construir una Content Factory integrada con datos reales de productos, servicios, campañas, clientes y canales, evitando procesos aislados y trabajo manual repetitivo.
> 

---

# 1. Objetivo

Construir una plataforma de marketing y contenido capaz de:

- planificar campañas;
- generar briefs;
- producir textos;
- producir imágenes y videos;
- adaptar contenido por canal;
- mantener identidad por marca;
- coordinar aprobaciones;
- programar publicaciones;
- medir rendimiento;
- reutilizar activos;
- automatizar tareas;
- integrar agentes IA;
- conectar marketing con ventas y resultados.

---

# 2. Alcance

La estrategia cubre:

- campañas;
- briefs;
- contenido escrito;
- diseño gráfico;
- video;
- animación;
- contenido 3D;
- generación de imágenes;
- generación de video;
- redes sociales;
- email;
- landing pages;
- tiendas;
- YouTube;
- SEO;
- Cloudinary;
- Figma;
- Adobe;
- Blender;
- ComfyUI;
- DaVinci Resolve;
- n8n;
- agentes IA;
- analítica;
- atribución;
- aprobación humana.

---

# 3. Principios

1. **Brand-first**
    
    Cada pieza debe respetar identidad, tono, público y objetivos de la marca.
    
2. **Data-driven**
    
    El contenido debe apoyarse en datos reales de productos, servicios, campañas y resultados.
    
3. **Human approval**
    
    La IA puede proponer y producir borradores, pero el contenido sensible debe ser aprobado.
    
4. **Reusable assets**
    
    Los activos deben almacenarse, versionarse y reutilizarse.
    
5. **Channel adaptation**
    
    Un mismo concepto debe adaptarse a cada canal.
    
6. **Automation with control**
    
    Automatizar tareas repetitivas sin perder revisión ni trazabilidad.
    
7. **Official APIs**
    
    Publicar mediante APIs oficiales cuando sea posible.
    
8. **Measurement**
    
    Toda campaña debe definir métricas.
    
9. **Progressive sophistication**
    
    Comenzar con flujos simples y evolucionar hacia producción multimedia avanzada.
    
10. **Portfolio evidence**
    
    Cada etapa debe generar piezas, flujos, dashboards y demos verificables.
    

---

# 4. Arquitectura general

```
Business Data
    │
    ├── Products
    ├── Services
    ├── Campaigns
    ├── Customers
    ├── Sales
    └── Brand Guidelines
    │
    ▼
Marketing and Content Layer
    │
    ├── Marketing Agent
    ├── Content Agent
    ├── SEO Agent
    ├── Social Media Agent
    ├── Design Workflow
    └── Approval Workflow
    │
    ▼
Creative Tools
    │
    ├── Figma
    ├── Adobe
    ├── Blender
    ├── ComfyUI
    ├── DaVinci Resolve
    └── Cloudinary
    │
    ▼
Channels
    ├── Web
    ├── Stores
    ├── Instagram
    ├── Facebook
    ├── LinkedIn
    ├── TikTok
    ├── YouTube
    ├── WhatsApp
    └── Email
```

---

# 5. Content Factory

## Objetivo

Crear un flujo industrializado y controlado de producción de contenido.

## Flujo

```
Campaign Objective
        ↓
Data and Audience
        ↓
Creative Brief
        ↓
Copy and Script
        ↓
Visual Production
        ↓
Review
        ↓
Approval
        ↓
Channel Adaptation
        ↓
Scheduling
        ↓
Publishing
        ↓
Measurement
        ↓
Optimization
```

## Componentes

- campaign planner;
- brand guidelines;
- content brief;
- copy generator;
- script generator;
- visual generator;
- asset library;
- approval workflow;
- scheduling;
- analytics;
- optimization.

---

# 6. Brand Guidelines

Cada marca debe tener una guía estructurada.

## Elementos

- propósito;
- posicionamiento;
- público;
- tono;
- personalidad;
- palabras permitidas;
- palabras prohibidas;
- colores;
- tipografías;
- logo;
- iconografía;
- estilo fotográfico;
- estilo de video;
- ejemplos;
- restricciones legales;
- claims permitidos.

## Regla

Los agentes deben consumir estas guías antes de generar contenido.

---

# 7. Campañas

## Entidad Campaign

Debe incluir:

- marca;
- nombre;
- objetivo;
- audiencia;
- canal;
- producto o servicio;
- presupuesto;
- fecha inicio;
- fecha fin;
- mensaje principal;
- CTA;
- KPI;
- owner;
- estado;
- assets;
- publicaciones;
- resultados.

## Estados

```
draft
planning
in_review
approved
scheduled
active
paused
completed
cancelled
```

---

# 8. Creative Brief

## Contenido

- problema;
- objetivo;
- audiencia;
- insight;
- propuesta de valor;
- mensaje;
- tono;
- formato;
- canal;
- CTA;
- restricciones;
- referencias;
- métricas;
- deadline.

## Automatización

El brief puede generarse con IA desde:

- datos de producto;
- datos de servicio;
- objetivo comercial;
- histórico de campañas;
- audiencia;
- temporada;
- canal.

---

# 9. Marketing Agent

## Responsabilidades futuras

- proponer campañas;
- detectar oportunidades;
- definir audiencias;
- generar briefs;
- analizar resultados;
- sugerir presupuesto;
- identificar canales;
- resumir métricas;
- recomendar optimizaciones.

## Límites

- no aprobar presupuesto;
- no publicar automáticamente campañas sensibles;
- no modificar precios;
- no prometer resultados;
- no usar datos no autorizados.

---

# 10. Content Agent

## Responsabilidades

- generar copys;
- generar titulares;
- generar guiones;
- adaptar tono;
- crear variantes;
- redactar descripciones;
- crear FAQs;
- generar metadata;
- resumir contenido;
- preparar prompts visuales.

## Controles

- brand guidelines;
- revisión humana;
- validación legal;
- versionado;
- trazabilidad;
- detección de contenido repetido.

---

# 11. Social Media Agent

## Responsabilidades

- adaptar contenido;
- proponer calendario;
- generar captions;
- generar hashtags;
- preparar variantes;
- recopilar métricas;
- detectar comentarios;
- responder casos simples;
- escalar casos sensibles.

## Regla

No responder automáticamente:

- reclamos graves;
- temas legales;
- información financiera;
- crisis;
- solicitudes sensibles.

---

# 12. SEO Agent

## Responsabilidades

- títulos;
- meta descriptions;
- briefs SEO;
- preguntas frecuentes;
- estructura;
- enlaces internos;
- análisis Search Console;
- oportunidades;
- errores;
- priorización de contenido.

## Controles

- no generar contenido masivo de baja calidad;
- no usar técnicas black-hat;
- no publicar sin revisión;
- basarse en datos reales.

---

# 13. Copywriting

## Tipos de contenido

- anuncios;
- publicaciones;
- emails;
- landing pages;
- descripciones;
- guiones;
- FAQs;
- artículos;
- mensajes WhatsApp;
- notificaciones;
- propuestas comerciales.

## Estructuras útiles

- AIDA;
- PAS;
- Before–After–Bridge;
- Problem–Solution;
- Storytelling;
- Feature–Benefit;
- Social Proof.

---

# 14. Visual Content

## Tipos

- fotografías;
- banners;
- carruseles;
- infografías;
- reels;
- stories;
- thumbnails;
- mockups;
- renders;
- animaciones;
- piezas 3D;
- videos cortos;
- videos largos.

---

# 15. Figma

## Rol

Diseño, prototipado y sistema visual.

## Casos

- plantillas;
- banners;
- social posts;
- landings;
- presentaciones;
- design system;
- componentes;
- handoff;
- automatización mediante API.

## Integración futura

- Figma API;
- generación de assets;
- duplicación de templates;
- actualización de textos;
- exportación;
- versionado.

---

# 16. Adobe Creative Cloud

## Herramientas

### Photoshop

- edición;
- retoque;
- composiciones;
- banners;
- mockups.

### Illustrator

- vectores;
- logos;
- iconografía;
- piezas escalables.

### Premiere Pro

- edición de video;
- contenido social;
- videos comerciales;
- demos.

### After Effects

- motion graphics;
- animación;
- intros;
- efectos;
- templates.

## Estado

- Planned;
- inversión futura;
- uso cuando la etapa de marketing lo justifique.

---

# 17. Alternativas gratuitas

| Tool | Uso |
| --- | --- |
| GIMP | Edición de imagen |
| Inkscape | Diseño vectorial |
| Krita | Ilustración |
| DaVinci Resolve | Video |
| Blender | 3D y animación |
| ComfyUI | Generación IA |
| Figma Free | Diseño y prototipado |

---

# 18. Blender

## Casos

- productos 3D;
- renders;
- animaciones;
- layouts;
- simulaciones;
- piezas publicitarias;
- visualización de locales;
- contenido comercial.

## Integración con PC de IA

El PC de IA será el equipo principal para:

- render;
- GPU;
- simulaciones;
- generación multimedia;
- workflows pesados.

---

# 19. ComfyUI

## Rol

Automatización local de generación visual.

## Casos

- imágenes de campaña;
- variaciones;
- fondos;
- estilos;
- mockups;
- thumbnails;
- contenido de producto;
- workflows reutilizables.

## Principios

- workflows versionados;
- prompts registrados;
- revisión humana;
- control de marca;
- no usar imágenes con derechos dudosos;
- no publicar automáticamente.

---

# 20. Video Production

## Flujo

```
Brief
  ↓
Script
  ↓
Storyboard
  ↓
Recording or Generation
  ↓
Editing
  ↓
Motion Graphics
  ↓
Review
  ↓
Export
  ↓
Publishing
```

## Herramientas

- DaVinci Resolve;
- Premiere Pro;
- After Effects;
- Blender;
- ComfyUI;
- YouTube;
- Cloudinary.

---

# 21. YouTube

## Casos

- contenido comercial;
- tutoriales;
- portafolio;
- demos;
- entrevistas;
- historias de marca;
- contenido SEO;
- videos educativos.

## Requisitos

- título;
- descripción;
- thumbnail;
- capítulos;
- subtítulos;
- tags;
- CTA;
- playlist;
- métricas.

---

# 22. Cloudinary

## Rol

Biblioteca y distribución de assets.

## Funciones

- almacenamiento;
- transformación;
- optimización;
- CDN;
- thumbnails;
- formatos;
- responsive images;
- metadata.

## Organización

```
brand/
├── products/
├── campaigns/
├── social/
├── video/
├── logos/
└── archived/
```

---

# 23. Digital Asset Management

## Entidad Asset

Debe incluir:

- marca;
- campaña;
- tipo;
- archivo;
- URL;
- versión;
- formato;
- dimensiones;
- duración;
- copyright;
- autor;
- estado;
- canal;
- fecha;
- metadata.

## Estados

```
draft
review
approved
published
archived
rejected
```

---

# 24. Content Calendar

## Datos

- fecha;
- canal;
- marca;
- campaña;
- pieza;
- owner;
- estado;
- hora;
- CTA;
- URL;
- resultados.

## Vistas

- calendario;
- kanban;
- por marca;
- por campaña;
- por canal;
- por responsable.

---

# 25. Scheduling

## Herramientas

- n8n;
- APIs oficiales;
- Meta API;
- YouTube Data API;
- LinkedIn API;
- TikTok API;
- email provider.

## Requisitos

- timezone;
- retries;
- errores;
- aprobación;
- logs;
- rate limits;
- estado de publicación.

---

# 26. n8n

## Rol

Orquestación de flujos de marketing.

## Casos

- recibir brief;
- generar contenido;
- crear tareas;
- solicitar aprobación;
- publicar;
- recopilar métricas;
- enviar reportes;
- sincronizar assets;
- notificar errores.

## Regla

n8n no debe ser el repositorio principal de contenido ni contener reglas críticas.

---

# 27. Publishing Workflow

```
Draft
  ↓
Brand Validation
  ↓
Legal Validation
  ↓
Approval
  ↓
Scheduling
  ↓
Publishing
  ↓
Verification
  ↓
Metrics
```

## Controles

- quién aprobó;
- versión;
- canal;
- fecha;
- resultado;
- URL publicada;
- error;
- rollback cuando sea posible.

---

# 28. Approval Workflow

## Niveles

| Risk | Approval |
| --- | --- |
| Bajo | Revisión simple |
| Medio | Aprobación del owner |
| Alto | Aprobación de marketing y negocio |
| Crítico | Aprobación legal o ejecutiva |

## Contenido crítico

- precios;
- promociones;
- salud;
- aspectos legales;
- promesas;
- finanzas;
- franquicias;
- información de clientes.

---

# 29. Content Repurposing

## Objetivo

Transformar una pieza en múltiples formatos.

## Ejemplo

```
Video largo
   ├── Reel
   ├── Short
   ├── Carrusel
   ├── Post
   ├── Blog
   ├── Newsletter
   └── Clip para tienda
```

## Beneficios

- mayor productividad;
- coherencia;
- menor costo;
- reutilización;
- mayor alcance.

---

# 30. Personalization

## Futuro

- contenido por segmento;
- recomendaciones;
- emails;
- ofertas;
- páginas dinámicas;
- campañas por comportamiento.

## Requisitos

- consentimiento;
- datos suficientes;
- segmentación;
- privacidad;
- medición;
- no discriminación.

---

# 31. Campaign Analytics

## Métricas

- alcance;
- impresiones;
- clics;
- CTR;
- conversiones;
- leads;
- ventas;
- engagement;
- costo;
- ROAS;
- CAC;
- frecuencia;
- retención;
- revenue.

---

# 32. Attribution

## Objetivo

Relacionar campañas con resultados.

## Datos

- UTM;
- channel;
- campaign;
- creative;
- lead;
- customer;
- order;
- revenue.

## Modelos

- first touch;
- last touch;
- linear;
- campaign-based;
- assisted.

---

# 33. Experimentation

## Tipos

- A/B testing;
- títulos;
- imágenes;
- CTA;
- landing;
- email subject;
- video thumbnail;
- horarios;
- audiencias.

## Requisitos

- hipótesis;
- métrica;
- tamaño suficiente;
- período;
- resultado;
- documentación.

---

# 34. Content Performance

## Métricas por pieza

- views;
- reach;
- engagement;
- watch time;
- clicks;
- conversions;
- saves;
- shares;
- comments;
- leads;
- revenue.

## Acciones

- optimizar;
- reutilizar;
- archivar;
- reemplazar;
- ampliar;
- detener.

---

# 35. Marketing Data Model

## Entidades

- campaign;
- audience;
- segment;
- brief;
- content;
- asset;
- publication;
- channel;
- metric;
- conversion;
- lead;
- experiment;
- approval.

---

# 36. Marketing Events

```
campaign.created
brief.approved
content.generated
content.approved
content.scheduled
content.published
content.failed
lead.created
conversion.completed
campaign.completed
```

---

# 37. Integration with Commerce

## Datos compartidos

- productos;
- servicios;
- precios;
- promociones;
- stock;
- ventas;
- pedidos;
- clientes;
- campañas.

## Casos

- campañas por producto;
- promoción por stock;
- contenido por temporada;
- abandono de carrito;
- cross-selling;
- remarketing;
- lanzamientos.

---

# 38. Integration with AI

## Casos

- briefs;
- copys;
- scripts;
- prompts;
- imágenes;
- video;
- SEO;
- segmentación;
- análisis;
- optimización;
- respuesta social.

## Regla

Los agentes deben utilizar información autorizada y no inventar atributos comerciales.

---

# 39. Marketing Knowledge Base

## Contenido

- brand guidelines;
- campañas;
- históricos;
- casos exitosos;
- audiencias;
- assets;
- mensajes;
- productos;
- restricciones;
- aprendizajes.

## Integración

- RAG;
- Notion;
- Confluence;
- Azure DevOps Wiki;
- Qdrant.

---

# 40. Legal and Compliance

## Controles

- copyright;
- licencias;
- uso de imagen;
- datos personales;
- claims;
- promociones;
- concursos;
- salud;
- publicidad;
- términos;
- consentimiento.

## Regla

Todo contenido regulado debe pasar revisión humana.

---

# 41. Security

## Controles

- permisos;
- secretos;
- APIs oficiales;
- tokens;
- accesos por marca;
- auditoría;
- aprobación;
- validación de webhooks;
- protección de assets;
- almacenamiento seguro.

---

# 42. QA

## Pruebas

- links;
- metadata;
- formatos;
- dimensiones;
- publicación;
- scheduling;
- UTM;
- tracking;
- accesibilidad;
- contenido;
- APIs;
- fallos;
- duplicados;
- aprobaciones.

---

# 43. Observability

## Métricas técnicas

- publicaciones exitosas;
- publicaciones fallidas;
- retries;
- latencia;
- API errors;
- rate limits;
- assets faltantes;
- webhooks;
- tiempo de aprobación.

## Métricas de negocio

- conversiones;
- revenue;
- engagement;
- leads;
- costo;
- ROAS.

---

# 44. Roadmap de implementación

## Etapa 1 — Base

1. brand guidelines;
2. modelo de campaña;
3. modelo de contenido;
4. asset library;
5. Cloudinary;
6. calendario;
7. aprobación.

## Etapa 2 — Producción

1. Figma;
2. templates;
3. copys;
4. video básico;
5. YouTube;
6. piezas sociales.

## Etapa 3 — Automatización

1. n8n;
2. scheduling;
3. métricas;
4. reporting;
5. alertas;
6. workflows de aprobación.

## Etapa 4 — IA

1. Marketing Agent;
2. Content Agent;
3. SEO Agent;
4. Social Media Agent;
5. ComfyUI;
6. generación multimedia.

## Etapa 5 — Avanzado

1. Adobe;
2. Blender;
3. content repurposing;
4. experimentación;
5. personalización;
6. atribución avanzada.

---

# 45. Prioridad actual

## Urgente

1. definir brand data;
2. definir asset model;
3. estructurar campañas;
4. preparar Cloudinary;
5. conectar contenido con canales;
6. definir approval workflow.

## Corto plazo

1. Figma templates;
2. calendario;
3. YouTube;
4. social content;
5. n8n;
6. métricas.

## Mediano plazo

1. Content Agent;
2. Marketing Agent;
3. ComfyUI;
4. video;
5. SEO Agent;
6. social automation.

## Largo plazo

1. Adobe;
2. Blender;
3. personalización;
4. experimentación avanzada;
5. atribución completa;
6. producción multimedia a escala.

---

# 46. Evidencia para portafolio

## Entregables

- Content Factory;
- workflow n8n;
- campaña completa;
- brand guidelines;
- Figma templates;
- assets versionados;
- generación IA;
- aprobación;
- publicación;
- dashboard;
- video;
- reporte de resultados.

---

# 47. Criterio de finalización

Una capacidad de marketing se considera implementada cuando:

1. tiene objetivo;
2. respeta la marca;
3. tiene owner;
4. tiene aprobación;
5. tiene assets versionados;
6. tiene canal;
7. tiene tracking;
8. tiene métricas;
9. tiene seguridad;
10. tiene documentación;
11. puede demostrarse.

---

# 48. Visión final

```
Business Data
      +
AI Agents
      +
Creative Tools
      +
Automation
      +
Approval
      +
Multichannel Publishing
      +
Analytics
```

SBM Suite debe evolucionar hacia una Content Factory multimarcas capaz de producir, adaptar, publicar y medir contenido de forma integrada, automatizada y controlada.

---

# 49. Dedicated SBM applications — 2026-08-16

| Project | Type | Selected technology | Responsibility |
|---|---|---|---|
| SBM-MARKETING | API | Node.js / TypeScript / NestJS | Social data, SEO, campaigns, calendars, photo/video sessions, promotion payments, equipment rentals, contracted services/providers and metrics |
| SBM-CONTENT | API/service | Python / FastAPI | Asset production, generation, editing and creative-tool workflows |

Named agents: `Belfort Agent` leads Marketing/Sales strategy; `Stratton Agent` manages MarTech/integrations/QA; `Donnie Agent` operates channels/chatbot/publications; `DaVinci Agent` generates creative work; `Medici Agent` performs independent creative QA/standards/trend review. `SBM-MARKETING` and `SBM-CONTENT` remain deterministic domain services; agents reason/orchestrate through authorized APIs rather than owning persistence directly.
