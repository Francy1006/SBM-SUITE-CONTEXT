# 📱 Digital Channels, SEO & Social Media

> Estrategia transversal de canales digitales, posicionamiento orgánico, analítica, contenido distribuido y presencia social para SBM Suite.
> 
> 
> Esta página define cómo cada marca podrá operar sitios web, tiendas, aplicaciones, redes sociales, mensajería, video, analítica y SEO desde una arquitectura común, manteniendo identidad propia, trazabilidad y conexión con los datos reales de la plataforma.
> 
> El objetivo no es solo publicar contenido, sino construir canales medibles, integrados y reutilizables.
> 

---

# 1. Objetivo

Construir una capa digital transversal que permita:

- publicar sitios y tiendas por marca;
- mejorar posicionamiento orgánico;
- administrar dominios y metadatos;
- integrar analítica;
- publicar contenido;
- operar redes sociales;
- conectar mensajería;
- reutilizar activos digitales;
- medir rendimiento;
- generar leads;
- conectar campañas con ventas;
- integrar agentes IA;
- mantener trazabilidad por marca y canal.

---

# 2. Alcance

La estrategia cubre:

- `KS-STORE`;
- `sbm-comercial`;
- `sbm-digital-api`;
- sitios corporativos;
- tiendas;
- landing pages;
- aplicaciones móviles futuras;
- Google Search Console;
- Google Analytics;
- Google Tag Manager;
- Lighthouse;
- PageSpeed Insights;
- YouTube;
- Cloudinary;
- WhatsApp;
- Instagram;
- Facebook;
- LinkedIn;
- TikTok;
- Microsoft Teams;
- Telegram;
- email;
- SEO;
- contenido;
- analítica;
- conversiones;
- campañas;
- integración con IA.

---

# 3. Principios

1. **Brand-specific presentation**
    
    Cada marca mantiene identidad, dominio, contenido y canales propios.
    
2. **Shared platform capabilities**
    
    SEO, analítica, multimedia, autenticación y publicación deben reutilizar capacidades comunes.
    
3. **API-first**
    
    Los canales consumen APIs; no escriben directamente en bases de datos.
    
4. **SEO by design**
    
    El posicionamiento debe formar parte de la arquitectura desde el inicio.
    
5. **Performance matters**
    
    La velocidad afecta experiencia, conversión y SEO.
    
6. **Measured channels**
    
    Todo canal relevante debe tener métricas.
    
7. **Content reuse**
    
    Un activo debe poder adaptarse a varios canales.
    
8. **Official APIs first**
    
    Las automatizaciones deben utilizar APIs oficiales cuando sea posible.
    
9. **Human approval**
    
    Publicaciones sensibles deben poder requerir aprobación.
    
10. **Privacy and consent**
    
    La medición debe respetar privacidad y consentimiento.
    

---

# 4. Arquitectura general

```
Brand Data and Content
        │
        ▼
SBM Suite
        │
        ├── Catalog
        ├── Products
        ├── Services
        ├── Campaigns
        ├── Digital Assets
        └── Brand Configuration
        │
        ▼
sbm-digital-api
        │
        ├── SEO Data
        ├── Channel Adaptation
        ├── Media URLs
        ├── Analytics Events
        ├── Public Content
        └── Rate Limiting
        │
        ▼
Digital Channels
        ├── Website
        ├── Store
        ├── Social Media
        ├── WhatsApp
        ├── YouTube
        ├── Email
        └── Mobile Apps
```

---

# 5. Canales digitales por marca

Cada marca puede activar de forma independiente:

- sitio corporativo;
- tienda;
- catálogo;
- blog;
- landing pages;
- formulario;
- WhatsApp;
- Instagram;
- Facebook;
- LinkedIn;
- TikTok;
- YouTube;
- email;
- marketplace;
- aplicación móvil;
- agenda;
- soporte.

## Configuración mínima

- canal;
- estado;
- URL;
- cuenta;
- identificador externo;
- credenciales seguras;
- owner;
- permisos;
- analytics;
- webhook;
- fecha de sincronización.

---

# 6. Sitios web

## Tipos

- corporativo;
- tienda;
- catálogo;
- portal de servicios;
- landing page;
- micrositio;
- portal de contenido.

## Requisitos

- responsive;
- accesible;
- indexable;
- rápido;
- seguro;
- configurable por marca;
- conectado a APIs;
- analítica;
- SEO;
- contenido administrable.

---

# 7. Stack recomendado

## Frontend

- React;
- TypeScript;
- Tailwind CSS;
- Vite o framework con SSR cuando corresponda.

## Backend digital

- Node.js;
- NestJS;
- `sbm-digital-api`.

## Backend de negocio

- `DP-API`;
- `SBM-API`;
- futuras APIs cliente.

## Multimedia

- Cloudinary;
- YouTube;
- object storage;
- CDN.

---

# 8. SEO técnico

## Elementos

- title;
- meta description;
- canonical;
- Open Graph;
- Twitter Cards;
- Schema.org;
- sitemap XML;
- robots.txt;
- breadcrumbs;
- hreflang futuro;
- URLs legibles;
- redirects;
- status codes;
- internal linking.

## Requisitos

- metadatos dinámicos;
- indexación controlada;
- no indexar ambientes de prueba;
- contenido renderizable;
- evitar duplicados;
- validación automática;
- performance.

---

# 9. SEO on-page

## Elementos

- encabezados;
- contenido útil;
- intención de búsqueda;
- descripciones;
- enlaces internos;
- imágenes;
- alt text;
- FAQs;
- llamadas a la acción;
- estructura semántica;
- datos estructurados.

## Principio

No crear contenido para llenar páginas. Cada página debe responder una intención real.

---

# 10. SEO off-page

## Acciones

- presencia de marca;
- perfiles oficiales;
- enlaces;
- menciones;
- partners;
- directorios relevantes;
- contenido compartible;
- reputación;
- reseñas.

## Regla

Evitar técnicas artificiales o enlaces de baja calidad.

---

# 11. Schema.org

## Tipos prioritarios

- Organization;
- LocalBusiness;
- Product;
- Offer;
- Service;
- FAQPage;
- BreadcrumbList;
- Article;
- VideoObject;
- Event;
- Review;
- AggregateRating.

## Implementación

Los schemas deben generarse desde datos reales de SBM Suite.

---

# 12. Sitemap

## Tipos

- sitemap general;
- sitemap de productos;
- sitemap de servicios;
- sitemap de contenido;
- sitemap de imágenes;
- sitemap de videos.

## Requisitos

- actualización automática;
- separación por marca;
- exclusión de contenido privado;
- URLs canónicas;
- envío a Search Console.

---

# 13. robots.txt

## Objetivo

Controlar crawling.

## Reglas

- bloquear staging;
- bloquear rutas administrativas;
- permitir recursos necesarios;
- enlazar sitemap;
- revisar por ambiente.

---

# 14. Google Search Console

## Uso

- indexación;
- cobertura;
- errores;
- consultas;
- páginas;
- Core Web Vitals;
- backlinks;
- sitemaps;
- inspección de URL.

## Integración futura

- paneles;
- reportes;
- alertas;
- agent summaries;
- priorización SEO.

---

# 15. Google Analytics

## Objetivo

Medir uso y conversión.

## Eventos

- page_view;
- product_view;
- service_view;
- add_to_cart;
- begin_checkout;
- purchase;
- lead_created;
- form_submitted;
- whatsapp_click;
- video_play;
- search;
- download;
- appointment_requested.

## Dimensiones

- marca;
- canal;
- campaña;
- producto;
- servicio;
- dispositivo;
- ubicación;
- fuente.

---

# 16. Google Tag Manager

## Uso

- etiquetas;
- eventos;
- conversiones;
- píxeles;
- marketing;
- pruebas controladas.

## Principio

No utilizar GTM para lógica de negocio.

---

# 17. Core Web Vitals

## Métricas

- Largest Contentful Paint;
- Interaction to Next Paint;
- Cumulative Layout Shift.

## Objetivos

- LCP menor a 2.5 s;
- INP menor a 200 ms;
- CLS menor a 0.1.

## Herramientas

- Lighthouse;
- PageSpeed Insights;
- Search Console;
- browser metrics.

---

# 18. Performance web

## Controles

- code splitting;
- lazy loading;
- image optimization;
- CDN;
- caching;
- compresión;
- tree shaking;
- minificación;
- critical CSS;
- SSR o pre-render;
- consultas eficientes;
- paginación.

---

# 19. Cloudinary

## Rol

Gestión de imágenes y multimedia.

## Casos

- imágenes de producto;
- logos;
- contenido;
- campañas;
- transformaciones;
- thumbnails;
- formatos modernos;
- CDN;
- optimización.

## Requisitos

- carpetas por marca;
- naming;
- metadata;
- versionado;
- acceso controlado;
- backups cuando corresponda.

---

# 20. Video

## Canales

- YouTube;
- Vimeo;
- Mux;
- Cloudflare Stream;
- almacenamiento propio.

## Uso recomendado

### YouTube

- demos;
- contenido público;
- tutoriales;
- videos de marca;
- portafolio.

### Vimeo

- presentación profesional;
- contenido restringido;
- campañas.

### Mux

- video programable;
- analítica;
- streaming.

### Cloudflare Stream

- video administrado;
- integración técnica.

---

# 21. YouTube

## Casos

- demostraciones técnicas;
- contenido de producto;
- tutoriales;
- contenido comercial;
- presentaciones;
- videos institucionales;
- evidencia de portafolio.

## Integración

- YouTube Data API;
- metadata;
- thumbnails;
- playlists;
- métricas;
- publicaciones.

---

# 22. Redes sociales

## Canales prioritarios

- Instagram;
- Facebook;
- LinkedIn;
- YouTube;
- TikTok;
- WhatsApp.

## Canales secundarios

- Telegram;
- X;
- Pinterest según marca.

## Principio

La selección depende del negocio, no de estar presente en todas las plataformas.

---

# 23. Instagram

## Casos

- productos;
- servicios;
- campañas;
- reels;
- historias;
- atención;
- leads;
- contenido visual.

## Integración

- Instagram Graph API;
- publicación;
- métricas;
- comentarios;
- mensajes según permisos;
- automatización controlada.

---

# 24. Facebook

## Casos

- páginas;
- campañas;
- publicaciones;
- eventos;
- leads;
- comunidades;
- anuncios;
- mensajería.

## Integración

- Meta Graph API;
- webhooks;
- métricas;
- contenido;
- campañas.

---

# 25. LinkedIn

## Casos

- posicionamiento profesional;
- servicios B2B;
- convenios;
- contenido técnico;
- empleo;
- partnerships;
- marca corporativa.

## Integración

- LinkedIn API;
- publicaciones;
- páginas;
- métricas según permisos.

---

# 26. TikTok

## Casos

- contenido corto;
- campañas;
- awareness;
- demostraciones;
- productos;
- alcance.

## Estado

- Research;
- sujeto a permisos;
- implementación posterior.

---

# 27. WhatsApp Business

## Rol

Canal comercial y de soporte.

## Casos

- consultas;
- catálogo;
- seguimiento;
- confirmaciones;
- recuperación de carrito;
- agenda;
- soporte;
- pedidos asistidos;
- notificaciones.

## Integración

- WhatsApp Business Platform;
- `SBM-AI-ASSISTANT`;
- `sbm-digital-api`;
- agentes;
- n8n.

---

# 28. Telegram

## Rol

Canal opcional para:

- bots;
- alertas;
- comunidades;
- pruebas multicanal;
- operaciones internas.

## Estado

- Research;
- Optional.

---

# 29. Microsoft Teams

## Rol

Canal empresarial futuro.

## Casos

- consultas internas;
- aprobaciones;
- alertas;
- agentes;
- procesos corporativos.

---

# 30. OpenClaw

## Rol

Gateway multicanal opcional.

## Canales

- Slack;
- WhatsApp;
- Telegram;
- Teams.

## Arquitectura

```
Digital Channel
      ↓
OpenClaw
      ↓
SBM-AI-ASSISTANT
      ↓
Tools / APIs / Agents
```

## Estado

- Research;
- Optional;
- posterior a integraciones prioritarias.

---

# 31. Email

## Casos

- campañas;
- transacciones;
- confirmaciones;
- alertas;
- newsletters;
- recuperación;
- onboarding;
- seguimiento.

## Requisitos

- templates;
- tracking controlado;
- consentimiento;
- unsubscribe;
- reputación;
- colas;
- retries;
- SPF;
- DKIM;
- DMARC.

---

# 32. Domains and DNS

## Configuración

- dominio;
- subdominios;
- DNS;
- correo;
- TLS;
- redirects;
- ambientes;
- verificación de servicios.

## Ejemplos

```
ditalypasta.cl
store.ditalypasta.cl
portalconvenios.cl
kiseki.cl
api.sbm-suite.cl
```

---

# 33. Brand identity

## Elementos

- logo;
- colores;
- tipografías;
- tono;
- imágenes;
- iconografía;
- plantillas;
- mensajes;
- estilo visual.

## Regla

La identidad debe almacenarse de forma estructurada y reusable.

---

# 34. Digital Asset Management

## Entidad

`DigitalAsset`

## Datos

- marca;
- tipo;
- archivo;
- URL;
- formato;
- tamaño;
- dimensiones;
- alt text;
- copyright;
- fecha;
- autor;
- estado;
- canal;
- campaña.

---

# 35. Content model

## Entidades

- page;
- article;
- post;
- campaign;
- asset;
- video;
- FAQ;
- landing;
- SEO metadata;
- channel publication.

## Estados

```
draft
review
approved
scheduled
published
archived
rejected
```

---

# 36. Content distribution

## Flujo

```
Content Brief
     ↓
Draft
     ↓
Review
     ↓
Approval
     ↓
Adaptation by Channel
     ↓
Scheduling
     ↓
Publishing
     ↓
Metrics
     ↓
Optimization
```

---

# 37. Social publishing

## Funciones

- programar;
- publicar;
- adaptar formatos;
- validar dimensiones;
- registrar URL;
- capturar métricas;
- detectar errores;
- reintentar;
- auditar.

## Regla

No depender de scraping si existe una API oficial.

---

# 38. Social listening

## Casos

- menciones;
- comentarios;
- sentimiento;
- preguntas;
- reputación;
- tendencias;
- oportunidades.

## Estado

- Planned;
- sujeto a APIs y permisos.

---

# 39. Leads

## Fuentes

- formularios;
- WhatsApp;
- redes;
- campañas;
- landing pages;
- email;
- marketplaces;
- eventos.

## Datos

- origen;
- campaña;
- marca;
- contacto;
- interés;
- estado;
- owner;
- consentimiento;
- historial.

---

# 40. Attribution

## Objetivo

Relacionar marketing con resultados.

## Modelos

- first touch;
- last touch;
- linear;
- campaign-based;
- assisted conversions.

## Datos

- UTM;
- referrer;
- campaign ID;
- channel;
- lead;
- order;
- customer.

---

# 41. UTM governance

## Campos

- `utm_source`;
- `utm_medium`;
- `utm_campaign`;
- `utm_content`;
- `utm_term`.

## Reglas

- naming estándar;
- catálogo de campañas;
- consistencia;
- documentación;
- no crear variantes arbitrarias.

---

# 42. Conversion tracking

## Conversiones

- venta;
- lead;
- reserva;
- descarga;
- llamada;
- WhatsApp;
- formulario;
- registro;
- visualización de producto;
- checkout.

## Requisitos

- evento;
- valor;
- moneda;
- marca;
- canal;
- campaña;
- consentimiento.

---

# 43. Privacy and consent

## Controles

- aviso de privacidad;
- consentimiento;
- cookies;
- categorías;
- opt-out;
- retención;
- anonimización;
- acceso;
- eliminación.

## Principio

No activar medición o marketing invasivo sin base legal y consentimiento cuando corresponda.

---

# 44. Accessibility

## Requisitos

- HTML semántico;
- teclado;
- contraste;
- foco;
- labels;
- alt text;
- formularios accesibles;
- mensajes de error;
- lectores de pantalla.

## Herramientas

- Lighthouse;
- axe-core;
- Playwright;
- browser tools.

---

# 45. Security

## Controles

- HTTPS;
- CSP;
- secure headers;
- rate limiting;
- anti-spam;
- validación;
- CAPTCHA cuando corresponda;
- protección de formularios;
- webhooks firmados;
- secretos;
- permisos;
- auditoría.

---

# 46. Analytics architecture

```
Digital Channel
      ↓
Events
      ↓
Google Tag Manager
      ↓
Google Analytics
      ↓
Business Data
      ↓
SBM Analytics
      ↓
Dashboards and Agents
```

---

# 47. Business dashboards

## Métricas

- tráfico;
- conversión;
- leads;
- ventas;
- engagement;
- contenido;
- canal;
- campaña;
- producto;
- servicio;
- marca;
- costo;
- retorno.

---

# 48. AI integration

## Casos

- generar metadatos;
- sugerir títulos;
- generar descripciones;
- adaptar contenido;
- resumir métricas;
- detectar oportunidades;
- generar briefs;
- clasificar leads;
- responder consultas;
- proponer mejoras SEO.

## Controles

- datos reales;
- aprobación;
- trazabilidad;
- revisión humana;
- no publicar automáticamente contenido sensible.

---

# 49. SEO Agent

## Responsabilidades futuras

- auditar páginas;
- detectar errores;
- proponer títulos;
- proponer descripciones;
- identificar contenido faltante;
- analizar Search Console;
- priorizar mejoras;
- generar reportes.

## Límites

- no modificar producción sin aprobación;
- no crear contenido masivo sin revisión;
- no aplicar técnicas riesgosas.

---

# 50. Social Media Agent

## Responsabilidades futuras

- preparar publicaciones;
- adaptar formatos;
- proponer calendario;
- generar borradores;
- recopilar métricas;
- responder casos simples;
- derivar casos sensibles.

---

# 51. Content Agent

## Responsabilidades futuras

- briefs;
- copys;
- guiones;
- variantes;
- SEO;
- prompts visuales;
- resúmenes;
- adaptación por canal.

---

# 52. Channel events

```
page.viewed
product.viewed
lead.created
form.submitted
whatsapp.clicked
video.played
content.published
campaign.started
conversion.completed
social.message.received
```

---

# 53. QA

## Pruebas

- metadata;
- sitemap;
- robots;
- structured data;
- links;
- responsive;
- accessibility;
- analytics events;
- forms;
- social links;
- performance;
- redirects;
- consent;
- security.

---

# 54. Observability

## Métricas

- availability;
- response time;
- Core Web Vitals;
- JS errors;
- API errors;
- conversion failures;
- form failures;
- publishing failures;
- webhook errors;
- social sync delay.

---

# 55. Roadmap de implementación

## Etapa 1 — Base digital

1. configuración de marca;
2. dominios;
3. metadatos;
4. Cloudinary;
5. analytics;
6. Search Console;
7. Tag Manager;
8. Lighthouse.

## Etapa 2 — `KS-STORE`

1. catálogo;
2. SEO;
3. sitemap;
4. structured data;
5. multimedia;
6. WhatsApp;
7. eventos;
8. conversiones.

## Etapa 3 — Canales sociales

1. Instagram;
2. Facebook;
3. LinkedIn;
4. YouTube;
5. programación;
6. métricas.

## Etapa 4 — Automatización

1. n8n;
2. agentes;
3. calendario;
4. aprobación;
5. publicación;
6. reporting.

## Etapa 5 — Omnicanal

1. WhatsApp Business;
2. OpenClaw;
3. Teams;
4. Telegram;
5. lead attribution;
6. social listening.

---

# 56. Prioridad actual

## Urgente

1. definir configuración digital por marca;
2. preparar SEO de `KS-STORE`;
3. implementar Cloudinary;
4. implementar Analytics;
5. implementar Search Console;
6. implementar Lighthouse;
7. definir eventos.

## Corto plazo

1. sitemap;
2. Schema.org;
3. WhatsApp;
4. YouTube;
5. Instagram;
6. Meta API;
7. panel de métricas.

## Mediano plazo

1. LinkedIn;
2. TikTok;
3. social publishing;
4. Content Agent;
5. SEO Agent;
6. attribution;
7. OpenClaw.

---

# 57. Evidencia para portafolio

## Entregables

- sitio indexable;
- Search Console;
- Lighthouse;
- PageSpeed;
- Schema.org;
- sitemap;
- analytics;
- dashboard;
- integración Cloudinary;
- publicación social;
- agente SEO;
- flujo multicanal;
- video demostrativo.

---

# 58. Criterio de finalización

Un canal digital se considera implementado cuando:

1. tiene configuración por marca;
2. tiene seguridad;
3. tiene analítica;
4. tiene SEO cuando corresponde;
5. tiene pruebas;
6. tiene observabilidad;
7. tiene documentación;
8. tiene contenido aprobado;
9. tiene métricas;
10. puede demostrarse.

---

# 59. Visión final

```
Brand Identity
      +
Web and Stores
      +
SEO
      +
Social Media
      +
Messaging
      +
Analytics
      +
AI Agents
```

SBM Suite debe evolucionar hacia una plataforma digital omnicanal donde cada marca pueda publicar, medir, automatizar y optimizar su presencia digital desde una arquitectura común y controlada.

---

# 60. Mobile/client channel naming — 2026-08-16

- `SBM-MOBILE`: SBM User.
- `KS-MOBILE`, `PC-MOBILE`, `CG-MOBILE`: Brand/Franchise User.
- `KS-CLIENT`, `PC-CLIENT`, `CG-CLIENT`: Client User.
- `PC-CUSTOMER`: PC Customer/patient.
- `KS-STORE`, `PC-STORE`, `CG-STORE`: public/end-customer web channels.

Mobile targets use React Native; exact features remain brand-specific and permission-scoped.
