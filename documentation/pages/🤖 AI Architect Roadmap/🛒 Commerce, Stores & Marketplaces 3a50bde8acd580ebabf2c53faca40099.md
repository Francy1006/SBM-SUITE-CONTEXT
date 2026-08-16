# 🛒 Commerce, Stores & Marketplaces

> **Nota de arquitectura 2026-08-16:** `sbm-comercial` y `sbm-digital-api` se conservan solo como conceptos históricos del roadmap. No son proyectos aprobados para crear actualmente; el diseño vigente prioriza APIs de marca + stores/mobile/client channels directos.
>
> Estrategia de comercio digital, tiendas, catálogo, pedidos y marketplaces para SBM Suite.
> 
> 
> Esta página define cómo cada marca podrá operar sus canales comerciales desde una plataforma común, manteniendo separación por marca, catálogo centralizado, sincronización de stock, precios, pedidos, clientes, contenidos y métricas.
> 
> La visión es construir una arquitectura omnicanal donde tiendas propias, aplicaciones, marketplaces, redes sociales y ventas presenciales consuman servicios comunes sin duplicar lógica de negocio.
> 

---

# 1. Objetivo

Construir una capa comercial transversal que permita:

- publicar catálogos;
- administrar productos y servicios;
- gestionar precios;
- gestionar stock;
- recibir pedidos;
- integrar pagos;
- administrar clientes;
- operar tiendas propias;
- conectar marketplaces;
- sincronizar canales;
- medir ventas;
- controlar contenido digital;
- mantener separación por marca;
- incorporar agentes IA comerciales.

---

# 2. Alcance

La estrategia cubre:

- `KS-STORE`;
- `sbm-comercial`;
- `sbm-digital-api`;
- `DP-API`;
- `SBM-API`;
- futuras APIs cliente;
- Mercado Libre;
- tiendas web;
- aplicaciones móviles;
- canales sociales;
- WhatsApp;
- ventas presenciales;
- catálogos;
- pedidos;
- clientes;
- stock;
- precios;
- promociones;
- contenidos;
- multimedia;
- analítica comercial.

---

# 3. Principios

1. **Platform-first**
    
    La solución comercial debe pertenecer a SBM Suite, no a desarrollos aislados por marca.
    
2. **Brand-aware**
    
    Todo catálogo, precio, stock, canal y pedido debe identificar su marca.
    
3. **API-first**
    
    Los canales comerciales deben consumir APIs y no acceder directamente a bases de datos.
    
4. **Omnichannel**
    
    Los distintos canales deben compartir información consistente.
    
5. **Single source of truth**
    
    Productos, precios, stock y pedidos deben tener una fuente oficial.
    
6. **Decoupled channels**
    
    Tiendas, apps y marketplaces no deben contener lógica crítica duplicada.
    
7. **SEO and performance**
    
    Las tiendas deben ser rápidas, indexables y accesibles.
    
8. **Security and privacy**
    
    Datos de clientes y transacciones deben protegerse.
    
9. **Human approval**
    
    Cambios de precio, publicaciones masivas y campañas sensibles deben poder requerir aprobación.
    
10. **Progressive implementation**
    
    `KS-STORE` será el primer caso real antes de generalizar la plataforma.
    

---

# 4. Arquitectura general

```
Customers and Channels
        │
        ├── Brand Store
        ├── Mobile App
        ├── Mercado Libre
        ├── WhatsApp
        ├── Social Media
        └── Physical Sales
        │
        ▼
sbm-digital-api
        │
        ├── Catalog Aggregation
        ├── Authentication
        ├── Rate Limiting
        ├── Cache
        ├── SEO Data
        ├── Media
        └── Channel Adaptation
        │
        ▼
Client API
        │
        └── DP-API
        │
        ▼
Internal Platform
        │
        └── SBM-API
```

---

# 5. Modelo de aplicaciones

## `KS-STORE`

Primera tienda pública de marca.

Responsabilidades:

- catálogo;
- productos;
- promociones;
- contenido;
- SEO;
- contacto;
- WhatsApp;
- carrito;
- pedidos;
- clientes;
- multimedia;
- integración con `DP-API`.

## `sbm-comercial`

Portal comercial transversal.

Responsabilidades:

- panel comercial;
- seguimiento de clientes;
- ventas;
- oportunidades;
- catálogo;
- campañas;
- pedidos;
- análisis comercial;
- gestión multimarcas.

## `sbm-digital-api`

BFF y Digital Experience API.

Responsabilidades:

- agregar respuestas;
- adaptar datos;
- proteger APIs internas;
- exponer canales públicos;
- cachear;
- aplicar rate limiting;
- manejar WebSockets o SSE;
- entregar contenido SEO;
- integrar multimedia;
- conectar marketplaces.

## `DP-API`

Primera API cliente.

Responsabilidades:

- productos;
- materiales;
- servicios;
- catálogos;
- precios;
- sucursales;
- proveedores;
- pedidos;
- clientes;
- tickets;
- datos públicos y de negocio de Ditaly Pasta.

## `SBM-API`

API interna transversal.

Responsabilidades:

- procesos críticos;
- configuración;
- lógica interna;
- control de marcas;
- integraciones transversales;
- procesos administrativos;
- inventario interno;
- cálculo;
- fiscal;
- operación.

---

# 6. Modelo por marca

Cada marca debe contar con una configuración central.

## Datos generales

- nombre comercial;
- razón social;
- dominio;
- subdominio;
- correo;
- teléfono;
- WhatsApp;
- dirección;
- logo;
- colores;
- tipografías;
- datos legales;
- redes sociales.

## Configuración digital

- canales activos;
- tienda activa;
- marketplace activo;
- métodos de pago;
- métodos de despacho;
- horarios;
- SEO;
- analytics;
- idioma;
- moneda;
- contenido;
- contacto.

## Configuración comercial

- listas de precios;
- catálogo;
- stock;
- promociones;
- condiciones;
- impuestos;
- comisiones;
- canales de venta.

---

# 7. Entidades principales

| Entity | Responsibility |
| --- | --- |
| Brand | Identidad comercial |
| Channel | Canal de venta |
| Catalog | Conjunto comercial |
| Product | Producto vendible |
| Service | Servicio vendible |
| Package | Agrupación comercial |
| Price List | Lista de precios |
| Price | Precio por contexto |
| Stock | Disponibilidad |
| Promotion | Regla promocional |
| Customer | Cliente |
| Cart | Carrito |
| Order | Pedido |
| Payment | Pago |
| Shipment | Despacho |
| Marketplace Listing | Publicación externa |
| Digital Asset | Imagen o video |
| SEO Configuration | Metadatos |
| Channel Configuration | Configuración por canal |

---

# 8. Catálogo

## Objetivo

Centralizar la información comercial de productos y servicios.

## Atributos

- código;
- SKU;
- nombre;
- descripción;
- categoría;
- tipo;
- unidad;
- marca;
- imágenes;
- videos;
- precio;
- stock;
- estado;
- disponibilidad;
- SEO;
- atributos;
- variantes;
- proveedor;
- canal.

## Requisitos

- versionado;
- estados;
- publicación programada;
- traducciones futuras;
- multimedia;
- filtros;
- búsqueda;
- auditoría.

---

# 9. Productos y variantes

## Producto base

Contiene la identidad comercial común.

## Variante

Representa diferencias como:

- tamaño;
- color;
- formato;
- sabor;
- presentación;
- capacidad;
- material;
- configuración.

## Regla

No duplicar productos completos cuando la diferencia corresponde a una variante.

---

# 10. Servicios

## Casos

- asesorías;
- trámites;
- operativos;
- convenios;
- servicios de salud;
- diseño;
- instalación;
- soporte;
- procesos administrativos.

## Atributos

- nombre;
- descripción;
- duración;
- alcance;
- ubicación;
- precio;
- requisitos;
- agenda;
- documentos;
- proveedor;
- disponibilidad.

---

# 11. Precios

## Tipos

- precio base;
- precio por canal;
- precio por sucursal;
- precio por cliente;
- precio promocional;
- precio mayorista;
- precio importación;
- precio dinámico sugerido;
- precio aprobado.

## Controles

- vigencia;
- moneda;
- impuestos;
- historial;
- auditoría;
- aprobación;
- fuente de costo;
- margen;
- redondeo.

---

# 12. Tipo de cambio

## Caso principal

Kiseki Tech.

## Flujo

```
Banco Central de Chile
        ↓
Tipo de cambio oficial
        ↓
Historial
        ↓
Costo de importación
        ↓
Margen
        ↓
Precio sugerido
        ↓
Aprobación
        ↓
Publicación
```

## Variables

- USD;
- transporte;
- aranceles;
- IVA;
- comisión;
- costo financiero;
- margen;
- marketplace;
- despacho;
- promoción.

---

# 13. Stock

## Objetivo

Mantener disponibilidad consistente por canal.

## Dimensiones

- marca;
- producto;
- variante;
- sucursal;
- bodega;
- canal;
- reservado;
- disponible;
- comprometido;
- dañado;
- en tránsito.

## Eventos

```
stock.updated
stock.reserved
stock.released
stock.adjusted
stock.transferred
stock.depleted
```

---

# 14. Inventario omnicanal

## Principio

Todos los canales deben consultar una fuente central.

## Controles

- reserva temporal;
- expiración;
- idempotencia;
- concurrencia;
- actualización por evento;
- reconciliación;
- auditoría;
- alertas.

---

# 15. Pedidos

## Estados

```
draft
pending
confirmed
paid
preparing
ready
shipped
delivered
cancelled
refunded
```

## Datos

- cliente;
- marca;
- canal;
- productos;
- precios;
- impuestos;
- descuentos;
- despacho;
- pago;
- estado;
- historial;
- documentos.

---

# 16. Flujo de pedido

```
Customer
   ↓
Channel
   ↓
Cart
   ↓
Validation
   ↓
Stock Reservation
   ↓
Price Confirmation
   ↓
Payment
   ↓
Order Confirmation
   ↓
Fulfillment
   ↓
Delivery
   ↓
Reconciliation
```

---

# 17. Carrito

## Requisitos

- persistencia;
- expiración;
- validación de stock;
- recálculo de precios;
- promociones;
- identificación de canal;
- recuperación de sesión;
- seguridad;
- auditoría mínima.

---

# 18. Clientes

## Datos

- identificación;
- nombre;
- correo;
- teléfono;
- dirección;
- preferencias;
- consentimiento;
- historial;
- canal;
- marca;
- segmento.

## Reglas

- minimización;
- privacidad;
- consentimiento;
- acceso restringido;
- separación por marca;
- eliminación o anonimización cuando corresponda.

---

# 19. Pagos

## Estrategia

Los pagos deben integrarse mediante adaptadores.

## Proveedores potenciales

- Webpay;
- Mercado Pago;
- Flow;
- Stripe;
- transferencias;
- pagos presenciales.

## Requisitos

- webhooks;
- idempotencia;
- conciliación;
- estados;
- reintentos;
- logs;
- no almacenar datos de tarjeta;
- cumplimiento del proveedor.

---

# 20. Despacho

## Modalidades

- retiro;
- despacho propio;
- courier;
- marketplace;
- entrega local;
- entrega programada;
- servicio en terreno.

## Datos

- dirección;
- zona;
- costo;
- ventana;
- proveedor;
- tracking;
- estado;
- evidencia.

---

# 21. Promociones

## Tipos

- descuento porcentual;
- descuento fijo;
- producto gratuito;
- bundle;
- cupón;
- precio por volumen;
- promoción por canal;
- promoción por fecha;
- promoción por cliente.

## Controles

- vigencia;
- prioridad;
- exclusiones;
- límites;
- combinación;
- aprobación;
- auditoría.

---

# 22. Mercado Libre

## Objetivo

Integrar Kiseki Tech y futuras marcas con Mercado Libre.

## Capacidades

- autenticación;
- publicaciones;
- categorías;
- atributos;
- imágenes;
- precios;
- stock;
- pedidos;
- preguntas;
- envíos;
- comisiones;
- reputación;
- conciliación.

## Flujo

```
SBM Catalog
    ↓
Marketplace Adapter
    ↓
Mercado Libre API
    ↓
Listing
    ↓
Orders and Events
    ↓
SBM Suite
```

---

# 23. Modelo de publicación en marketplace

## Entidad

`MarketplaceListing`

## Datos

- marketplace;
- account;
- product;
- external ID;
- title;
- description;
- category;
- price;
- stock;
- status;
- URL;
- fees;
- last sync;
- errors.

---

# 24. Sincronización

## Datos sincronizados

- producto;
- descripción;
- imágenes;
- precio;
- stock;
- estado;
- pedidos;
- preguntas;
- despacho.

## Requisitos

- retries;
- rate limits;
- idempotencia;
- eventos;
- logs;
- reconciliación;
- alertas;
- actualización parcial.

---

# 25. Marketplace Adapter

## Objetivo

Evitar acoplar SBM Suite a un marketplace específico.

## Interfaz conceptual

```
publish_product()
update_price()
update_stock()
pause_listing()
get_orders()
get_questions()
get_fees()
get_status()
```

## Futuro

- Mercado Libre;
- Amazon;
- Falabella;
- Ripley;
- otros marketplaces.

---

# 26. Tiendas propias

## Requisitos

- SSR o generación estática cuando aporte SEO;
- responsive;
- accesibilidad;
- rendimiento;
- seguridad;
- catálogo;
- carrito;
- checkout;
- analytics;
- contenido;
- búsqueda;
- filtros;
- multimedia.

## Tecnologías

- React;
- TypeScript;
- Tailwind;
- `sbm-digital-api`;
- Cloudinary;
- Google Analytics;
- Search Console;
- Lighthouse.

---

# 27. SEO

## Elementos

- title;
- meta description;
- canonical;
- Open Graph;
- Schema.org;
- sitemap;
- robots;
- URLs legibles;
- contenido indexable;
- performance;
- Core Web Vitals.

## Datos estructurados

- Product;
- Offer;
- Organization;
- LocalBusiness;
- Service;
- FAQ;
- BreadcrumbList.

---

# 28. Multimedia

## Herramientas

- Cloudinary;
- YouTube;
- Vimeo;
- Mux;
- Cloudflare Stream;
- almacenamiento local;
- object storage.

## Requisitos

- optimización;
- formatos modernos;
- responsive images;
- compresión;
- alt text;
- lazy loading;
- CDN;
- metadata;
- versionado.

---

# 29. Search

## Capacidades

- búsqueda textual;
- filtros;
- categorías;
- atributos;
- búsqueda semántica futura;
- sugerencias;
- ranking;
- sinónimos.

## Futuro

- Qdrant;
- embeddings;
- recomendaciones;
- personalización.

---

# 30. Recomendaciones

## Etapas

1. productos relacionados;
2. reglas de negocio;
3. productos populares;
4. segmentación;
5. content-based filtering;
6. collaborative filtering;
7. embeddings.

## Regla

No implementar modelos complejos sin datos suficientes.

---

# 31. WhatsApp Commerce

## Casos

- consultas;
- catálogo;
- atención;
- confirmación;
- seguimiento;
- recuperación de carrito;
- notificaciones;
- pedidos asistidos.

## Integración

- WhatsApp Business Platform;
- `SBM-AI-ASSISTANT`;
- `sbm-digital-api`;
- agentes comerciales;
- aprobación humana.

---

# 32. Social Commerce

## Canales

- Instagram;
- Facebook;
- TikTok;
- YouTube;
- LinkedIn para servicios;
- WhatsApp.

## Casos

- publicaciones;
- campañas;
- contenido;
- enlaces a productos;
- métricas;
- atención;
- leads.

---

# 33. Tiendas físicas y ventas presenciales

## Integración futura

- POS;
- pedidos manuales;
- stock;
- clientes;
- pagos;
- boletas;
- retiros;
- devoluciones.

## Principio

Las ventas presenciales deben alimentar la misma fuente comercial.

---

# 34. Devoluciones y reembolsos

## Estados

- requested;
- approved;
- rejected;
- received;
- refunded;
- exchanged;
- closed.

## Requisitos

- motivo;
- evidencia;
- producto;
- pago;
- stock;
- auditoría;
- documento tributario cuando corresponda.

---

# 35. Atención al cliente

## Canales

- tienda;
- correo;
- WhatsApp;
- Slack interno;
- marketplace;
- formulario;
- teléfono.

## Capacidades

- tickets;
- seguimiento;
- clasificación;
- SLA;
- respuestas;
- historial;
- agente IA;
- escalamiento humano.

---

# 36. Analítica comercial

## Métricas

- ventas;
- conversión;
- ticket promedio;
- abandono;
- productos;
- margen;
- stock;
- devoluciones;
- canal;
- cliente;
- campaña;
- marketplace;
- comisiones;
- costo de adquisición.

---

# 37. Eventos comerciales

```
catalog.published
product.viewed
cart.created
cart.abandoned
order.created
payment.confirmed
order.shipped
order.delivered
refund.created
listing.updated
customer.created
```

## Uso

- automatización;
- analítica;
- marketing;
- agentes;
- notificaciones;
- sincronización.

---

# 38. Integración con IA

## Casos

- búsqueda semántica;
- recomendaciones;
- generación de descripciones;
- SEO;
- respuestas de clientes;
- análisis de preguntas;
- pricing sugerido;
- forecast;
- detección de anomalías;
- resumen comercial.

## Controles

- aprobación;
- trazabilidad;
- datos reales;
- no publicar automáticamente sin reglas;
- validación de marca;
- seguridad.

---

# 39. Agentes comerciales

## Futuros agentes

- Sales Agent;
- Marketplace Agent;
- Customer Service Agent;
- Pricing Agent;
- Inventory Agent;
- Marketing Agent;
- Content Agent;
- Analytics Agent.

## Principio

Los agentes consumen APIs y tools autorizadas; no escriben directamente en base de datos.

---

# 40. Seguridad

## Controles

- autenticación;
- autorización;
- cifrado;
- rate limiting;
- protección de clientes;
- validación de webhooks;
- idempotencia;
- prevención de fraude;
- logs;
- permisos por marca;
- secretos;
- auditoría.

---

# 41. QA

## Pruebas

- catálogo;
- producto;
- variante;
- precio;
- stock;
- carrito;
- pedido;
- pago;
- despacho;
- promoción;
- marketplace;
- SEO;
- performance;
- accesibilidad;
- seguridad;
- contratos.

---

# 42. Performance

## Objetivos

- carga rápida;
- imágenes optimizadas;
- caché;
- CDN;
- consultas eficientes;
- paginación;
- lazy loading;
- SSR o estático cuando corresponda.

## Métricas

- LCP;
- INP;
- CLS;
- TTFB;
- p95 API;
- error rate;
- conversion rate.

---

# 43. Observabilidad

## Métricas

- pedidos;
- errores;
- pagos;
- stock;
- sincronizaciones;
- marketplace lag;
- latencia;
- webhooks;
- abandono;
- conversión;
- comisiones;
- fallas por canal.

---

# 44. Roadmap de implementación

## Etapa 1 — Base comercial

1. configuración de marca;
2. catálogo;
3. productos;
4. materiales;
5. precios;
6. stock;
7. APIs;
8. QA.

## Etapa 2 — `KS-STORE`

1. diseño;
2. catálogo público;
3. SEO;
4. multimedia;
5. contacto;
6. WhatsApp;
7. analytics;
8. despliegue.

## Etapa 3 — Pedidos

1. carrito;
2. clientes;
3. pedido;
4. stock reservado;
5. pago;
6. despacho;
7. notificaciones.

## Etapa 4 — `sbm-digital-api`

1. BFF;
2. caché;
3. rate limiting;
4. agregación;
5. SEO;
6. canales;
7. observabilidad.

## Etapa 5 — Marketplaces

1. Mercado Libre;
2. publicaciones;
3. precios;
4. stock;
5. pedidos;
6. preguntas;
7. conciliación.

## Etapa 6 — Omnicanal

1. WhatsApp;
2. redes;
3. POS;
4. apps;
5. agentes;
6. recomendaciones;
7. analítica avanzada.

---

# 45. Prioridad actual

## Urgente

1. estabilizar `product`;
2. estabilizar `material`;
3. completar separación `SBM-API` / `DP-API`;
4. definir configuración de marca;
5. documentar contratos;
6. QA;
7. seguridad.

## Corto plazo

1. `KS-STORE`;
2. catálogo público;
3. SEO;
4. multimedia;
5. clientes;
6. pedidos;
7. stock.

## Mediano plazo

1. `sbm-digital-api`;
2. pagos;
3. despacho;
4. Mercado Libre;
5. WhatsApp;
6. analítica.

## Largo plazo

1. otros marketplaces;
2. POS;
3. recomendaciones;
4. pricing inteligente;
5. agentes comerciales;
6. automatización omnicanal.

---

# 46. Evidencia para portafolio

## Entregables

- tienda pública;
- API documentada;
- catálogo multimarcas;
- flujo de pedido;
- sincronización Mercado Libre;
- pricing por USD;
- dashboard comercial;
- pruebas E2E;
- Lighthouse;
- arquitectura omnicanal;
- demo en video.

---

# 47. Criterio de finalización

Una capacidad comercial se considera implementada cuando:

1. tiene fuente oficial;
2. está separada por marca;
3. tiene contrato;
4. tiene pruebas;
5. tiene seguridad;
6. tiene observabilidad;
7. tiene documentación;
8. tiene manejo de errores;
9. tiene reconciliación cuando corresponde;
10. puede demostrarse.

---

# 48. Visión final

```
Central Catalog
      +
Brand Stores
      +
Marketplaces
      +
Social Channels
      +
Physical Sales
      +
Unified Orders
      +
Unified Stock
      +
Commercial AI Agents
```

SBM Suite debe evolucionar hacia una plataforma comercial omnicanal donde cada marca pueda operar sus tiendas, marketplaces y canales digitales desde una arquitectura centralizada, segura y escalable.

---

# 49. Brand commerce channels — 2026-08-16

Production-target stores are `KS-STORE`, `PC-STORE` and `CG-STORE`, implemented as brand public Ticket vitrines/channels consuming their canonical APIs. Catalog is the internal BOM/composition; Ticket is the sellable/reportable/scheduled commercial unit. Ditaly remains the historical reference and does not require a new production store.

---

## Legacy digital roadmap concepts

`sbm-comercial` and `sbm-digital-api` remain historical roadmap concepts, not current approved project-creation objectives. The current target favors direct brand APIs plus brand stores/client/mobile channels. Reactivate a transversal commercial portal/BFF only if a concrete cross-brand requirement justifies it.
