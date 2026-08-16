# 🧠 Machine Learning & Deep Learning

> Roadmap de Machine Learning y Deep Learning aplicado a SBM Suite.
> 
> 
> Esta página define los conocimientos, herramientas, casos de negocio, flujo de trabajo y criterios de implementación para incorporar modelos predictivos y analíticos dentro de la plataforma.
> 
> La prioridad es utilizar ML y DL solo cuando exista un problema real, datos suficientes y una mejora demostrable frente a reglas tradicionales.
> 

---

# 1. Objetivo

Incorporar capacidades de Machine Learning y Deep Learning dentro de SBM Suite para:

- predecir demanda;
- proyectar ventas;
- optimizar inventario;
- sugerir precios;
- detectar anomalías;
- segmentar clientes;
- recomendar productos;
- clasificar documentos;
- ejecutar OCR;
- analizar campañas;
- anticipar problemas operativos;
- apoyar decisiones financieras;
- automatizar tareas basadas en datos.

---

# 2. Principios

1. **Business-first**
    
    El modelo debe resolver un problema empresarial concreto.
    
2. **Baseline-first**
    
    Antes de entrenar un modelo complejo se debe comparar contra una regla simple.
    
3. **Data quality before model complexity**
    
    La calidad de los datos tiene prioridad sobre el algoritmo.
    
4. **Explainability**
    
    Las predicciones deben ser comprensibles cuando impacten decisiones relevantes.
    
5. **Human validation**
    
    Las recomendaciones críticas deben ser revisadas por una persona.
    
6. **Reproducibility**
    
    Datos, código, parámetros y resultados deben poder reproducirse.
    
7. **Monitoring**
    
    Los modelos deben monitorearse después del despliegue.
    
8. **Progressive complexity**
    
    Se comienza con ML clásico y solo se utiliza Deep Learning cuando sea necesario.
    
9. **Cost control**
    
    Se priorizan herramientas gratuitas, locales o con plan gratuito.
    
10. **Portfolio evidence**
    
    Cada caso debe producir evidencia técnica verificable.
    

---

# 3. Estado actual

Actualmente el trabajo de ML y DL se encuentra principalmente en fase de formación.

## Conocimientos y herramientas en aprendizaje

- NumPy;
- Pandas;
- Scikit-learn;
- TensorFlow;
- Keras;
- regresión lineal;
- regresión logística;
- clasificación;
- redes neuronales;
- embeddings;
- Word2Vec;
- CountVectorizer;
- procesamiento de texto;
- train/test split;
- métricas;
- normalización;
- feature engineering;
- OCR básico;
- notebooks en Google Colab.

## Estado dentro de SBM Suite

Aún no existe un modelo de Machine Learning desplegado como parte crítica de la plataforma.

Los primeros casos se implementarán cuando:

- existan datos suficientes;
- el núcleo transaccional esté estable;
- QA y seguridad estén implementados;
- la arquitectura de datos esté documentada;
- exista una métrica clara de éxito.

---

# 4. Flujo completo de Machine Learning

```
Problema de negocio
        ↓
Definición de métrica
        ↓
Obtención de datos
        ↓
Validación y calidad
        ↓
Análisis exploratorio
        ↓
Baseline
        ↓
Feature Engineering
        ↓
Entrenamiento
        ↓
Evaluación
        ↓
Validación de negocio
        ↓
Versionado
        ↓
Despliegue
        ↓
Monitoreo
        ↓
Reentrenamiento
```

---

# 5. Tipos de problemas

| Tipo | Ejemplos en SBM Suite |
| --- | --- |
| Regression | Ventas futuras, demanda, costos, tiempos |
| Classification | Riesgo, tipo de documento, prioridad de ticket |
| Clustering | Segmentación de clientes o sucursales |
| Time Series | Forecasting de ventas, stock y caja |
| Anomaly Detection | Ventas atípicas, errores de inventario, fraude |
| Recommendation | Productos, servicios, promociones |
| NLP | Clasificación, extracción y análisis de texto |
| Computer Vision | OCR, análisis de documentos y planos |
| Optimization | Inventario, rutas, precios y recursos |

---

# 6. Casos de uso prioritarios

## 1. Predicción de demanda

### Objetivo

Estimar la demanda futura de productos o materiales.

### Variables potenciales

- ventas históricas;
- día de la semana;
- mes;
- feriados;
- clima;
- sucursal;
- promociones;
- inventario;
- estacionalidad;
- eventos;
- precio.

### Modelos iniciales

- promedio móvil;
- regresión;
- Random Forest;
- XGBoost;
- modelos de series de tiempo.

### Resultado esperado

- compras más precisas;
- menos quiebres de stock;
- menos desperdicio;
- mejor planificación.

---

## 2. Forecasting de ventas

### Objetivo

Proyectar ventas por marca, sucursal, producto o período.

### Aplicaciones

- planificación;
- presupuestos;
- metas;
- compras;
- dotación;
- flujo de caja.

### Modelos

- regresión;
- ARIMA;
- Prophet como alternativa conceptual;
- XGBoost;
- redes neuronales solo si el volumen lo justifica.

---

## 3. Optimización de inventario

### Objetivo

Recomendar niveles mínimos y máximos de inventario.

### Variables

- demanda;
- lead time;
- seguridad;
- caducidad;
- costo;
- rotación;
- proveedor;
- estacionalidad.

### Resultado esperado

- sugerencias de reposición;
- alertas;
- reducción de sobrestock;
- reducción de quiebres.

---

## 4. Sugerencia de precios

### Objetivo

Generar precios recomendados sin publicar automáticamente cambios críticos.

### Variables

- costo;
- tipo de cambio;
- margen objetivo;
- demanda;
- stock;
- competencia;
- comisión;
- transporte;
- impuestos;
- estacionalidad.

### Control

Las recomendaciones deben requerir aprobación humana antes de publicarse.

---

## 5. Detección de anomalías

### Casos

- ventas inusuales;
- diferencias de inventario;
- precios fuera de rango;
- compras atípicas;
- errores de facturación;
- actividad sospechosa;
- cambios inesperados en métricas.

### Modelos

- Isolation Forest;
- Local Outlier Factor;
- reglas estadísticas;
- autoencoders en etapas avanzadas.

---

## 6. Segmentación de clientes

### Objetivo

Agrupar clientes según comportamiento.

### Variables

- frecuencia;
- recencia;
- monto;
- servicios utilizados;
- ubicación;
- canal;
- interacción.

### Técnicas

- RFM;
- K-Means;
- clustering jerárquico;
- DBSCAN.

---

## 7. Recomendación de productos o servicios

### Objetivo

Sugerir opciones relevantes según contexto.

### Casos

- productos relacionados;
- promociones;
- servicios de bienestar;
- complementos;
- catálogo personalizado.

### Técnicas

- reglas de asociación;
- collaborative filtering;
- content-based filtering;
- embeddings.

---

## 8. Clasificación documental

### Objetivo

Clasificar automáticamente documentos empresariales.

### Ejemplos

- factura;
- patente;
- resolución sanitaria;
- contrato;
- permiso;
- plano;
- certificado;
- expediente.

### Técnicas

- TF-IDF;
- modelos clásicos;
- embeddings;
- transformers;
- OCR más clasificación.

---

## 9. OCR

### Casos

- facturas;
- formularios;
- permisos;
- documentos escaneados;
- etiquetas;
- comprobantes;
- planos con texto.

### Flujo

```
Documento
   ↓
OCR
   ↓
Limpieza
   ↓
Extracción
   ↓
Validación
   ↓
Clasificación
   ↓
Almacenamiento
```

---

## 10. Análisis de campañas

### Objetivo

Medir y predecir rendimiento de campañas.

### Métricas

- alcance;
- clics;
- conversiones;
- costo;
- ventas;
- engagement;
- retorno;
- canal;
- audiencia.

### Casos

- predicción de conversión;
- segmentación;
- recomendación de contenido;
- detección de campañas ineficientes.

---

# 7. Machine Learning clásico

## Herramientas

| Technology | Uso |
| --- | --- |
| Scikit-learn | Modelos clásicos y pipelines |
| XGBoost | Boosting tabular |
| LightGBM | Modelos eficientes |
| CatBoost | Datos categóricos |
| Optuna | Optimización de hiperparámetros |
| Pandas | Preparación de datos |
| NumPy | Cálculo numérico |
| Polars | Procesamiento eficiente |
| DuckDB | Analítica local |

## Algoritmos prioritarios

- Linear Regression;
- Logistic Regression;
- Decision Trees;
- Random Forest;
- Gradient Boosting;
- XGBoost;
- K-Nearest Neighbors;
- Support Vector Machines;
- K-Means;
- DBSCAN;
- Isolation Forest;
- PCA.

---

# 8. Deep Learning

## Herramientas

| Technology | Uso |
| --- | --- |
| TensorFlow | Entrenamiento y despliegue |
| Keras | Construcción de redes |
| PyTorch | Investigación y modelos modernos |
| ONNX | Interoperabilidad |
| ONNX Runtime | Inferencia |
| TensorBoard | Visualización |
| Netron | Inspección de modelos |

## Arquitecturas

- Multilayer Perceptron;
- CNN;
- RNN;
- LSTM;
- GRU;
- Transformers;
- Autoencoders;
- Embedding Networks.

## Cuándo utilizar Deep Learning

Solo cuando:

- los datos sean suficientes;
- ML clásico no alcance el rendimiento esperado;
- exista una necesidad de visión, audio o NLP avanzado;
- el costo de entrenamiento e inferencia esté justificado;
- exista capacidad de monitoreo y mantenimiento.

---

# 9. Computer Vision

## Casos futuros

- OCR;
- clasificación de documentos;
- detección de objetos;
- lectura de etiquetas;
- revisión de fotografías;
- análisis de locales;
- inspección visual;
- asistencia con planos.

## Herramientas

- OpenCV;
- YOLO;
- PyTorch;
- TensorFlow;
- Label Studio;
- CVAT;
- Hugging Face.

## Flujo de datos

```
Captura
   ↓
Anotación
   ↓
Preprocesamiento
   ↓
Entrenamiento
   ↓
Evaluación
   ↓
Inferencia
   ↓
Validación humana
```

---

# 10. NLP

## Casos

- clasificación de textos;
- extracción de entidades;
- búsqueda semántica;
- análisis de solicitudes;
- resumen;
- routing;
- clasificación de tickets;
- análisis de comentarios;
- documentos.

## Herramientas

- NLTK;
- spaCy;
- Scikit-learn;
- Hugging Face Transformers;
- Sentence Transformers;
- embeddings;
- Qdrant.

## Técnicas

- tokenización;
- TF-IDF;
- Word2Vec;
- embeddings;
- Named Entity Recognition;
- classification;
- semantic similarity;
- transformers.

---

# 11. Time Series

## Casos

- ventas;
- demanda;
- inventario;
- precios;
- flujo de caja;
- operativos;
- citas;
- campañas.

## Técnicas

- moving average;
- exponential smoothing;
- ARIMA;
- feature-based forecasting;
- XGBoost;
- LSTM en etapas avanzadas.

## Requisitos

- frecuencia consistente;
- historial suficiente;
- control de faltantes;
- manejo de outliers;
- separación temporal;
- evaluación walk-forward.

---

# 12. Data Preparation

## Etapas

1. extracción;
2. limpieza;
3. tipificación;
4. validación;
5. tratamiento de faltantes;
6. outliers;
7. encoding;
8. normalización;
9. feature engineering;
10. separación de datos;
11. versionado.

## Fuentes potenciales

- PostgreSQL;
- eventos Kafka;
- archivos;
- APIs;
- CRM;
- inventario;
- ventas;
- campañas;
- marketplaces;
- documentos;
- logs.

---

# 13. Feature Engineering

## Ejemplos

- ventas por día;
- promedio móvil;
- días desde última compra;
- frecuencia de compra;
- margen;
- rotación;
- lead time;
- feriado;
- campaña activa;
- sucursal;
- marca;
- canal;
- tipo de cliente;
- variación de USD;
- stock disponible;
- tendencia;
- estacionalidad.

---

# 14. Evaluación de modelos

## Classification

- Accuracy;
- Precision;
- Recall;
- F1;
- ROC-AUC;
- PR-AUC;
- confusion matrix.

## Regression

- MAE;
- MSE;
- RMSE;
- MAPE;
- R².

## Ranking y recomendación

- [Precision@K](mailto:Precision@K);
- [Recall@K](mailto:Recall@K);
- NDCG;
- MAP.

## Time Series

- MAE;
- RMSE;
- MAPE;
- backtesting;
- walk-forward validation.

## Criterio empresarial

La métrica técnica debe relacionarse con:

- ahorro;
- ventas;
- tiempo;
- inventario;
- riesgo;
- calidad;
- conversión;
- error operativo.

---

# 15. Experiment Tracking

## Herramientas

- MLflow;
- TensorBoard;
- Weights & Biases Free;
- Comet Free;
- notebooks versionados.

## Información registrada

- dataset;
- versión;
- features;
- parámetros;
- modelo;
- métricas;
- artefactos;
- fecha;
- autor;
- entorno;
- resultado.

---

# 16. Data and Model Versioning

## Herramientas

- Git;
- DVC;
- MLflow;
- object storage;
- MinIO;
- Azure Blob Storage en etapas futuras.

## Artefactos

- datasets;
- modelos;
- configuraciones;
- notebooks;
- pipelines;
- métricas;
- reportes;
- features.

---

# 17. MLOps Architecture

```
Data Sources
     ↓
Data Pipeline
     ↓
Feature Preparation
     ↓
Training
     ↓
Experiment Tracking
     ↓
Model Registry
     ↓
Validation
     ↓
Deployment
     ↓
Monitoring
     ↓
Retraining
```

## Componentes

- data pipeline;
- experiment tracking;
- model registry;
- serving;
- monitoring;
- drift detection;
- retraining;
- rollback;
- CI/CD.

---

# 18. Model Serving

## Opciones

- FastAPI;
- dedicated inference service;
- ONNX Runtime;
- vLLM para LLM;
- batch inference;
- asynchronous inference;
- Kubernetes deployment.

## Principios

- no cargar modelos pesados innecesariamente dentro de APIs críticas;
- separar inferencia cuando exista necesidad;
- definir timeout;
- usar caché;
- versionar endpoints;
- monitorear latencia;
- permitir rollback.

---

# 19. Model Monitoring

## Métricas

- latencia;
- errores;
- volumen;
- distribución de entradas;
- distribución de predicciones;
- data drift;
- model drift;
- accuracy real;
- uso;
- costo.

## Herramientas

- Evidently AI;
- MLflow;
- Prometheus;
- Grafana;
- OpenTelemetry;
- logging estructurado.

---

# 20. Retraining

## Estrategias

- programado;
- por volumen de datos;
- por caída de rendimiento;
- por drift;
- manual;
- por cambio de negocio.

## Controles

- validación previa;
- comparación contra modelo actual;
- aprobación;
- rollback;
- versionado;
- auditoría.

---

# 21. Notebooks and Learning Environments

| Tool | Uso |
| --- | --- |
| JupyterLab | Desarrollo local |
| Google Colab Free | Entrenamiento y aprendizaje |
| Kaggle Notebooks | Datasets y experimentación |
| VS Code Notebooks | Integración con repositorios |
| Hugging Face Spaces | Demos |
| Obsidian | Notas y conocimiento |
| NotebookLM | Estudio asistido |

---

# 22. Obsidian

## Objetivo

Utilizar Obsidian como sistema personal de conocimiento para ML, DL e IA.

## Contenido

- conceptos;
- algoritmos;
- fórmulas;
- experimentos;
- errores;
- snippets;
- papers;
- cursos;
- comparaciones;
- decisiones;
- conexiones con SBM Suite.

## Integración futura

- Obsidian MCP;
- consulta desde agentes;
- búsqueda semántica;
- sincronización controlada;
- generación de notas.

---

# 23. Datasets

## Fuentes

- datos reales anonimizados;
- datasets sintéticos;
- Kaggle;
- Hugging Face Datasets;
- datos públicos;
- generación controlada.

## Requisitos

- sin información sensible;
- documentación;
- licencia;
- versionado;
- calidad;
- trazabilidad;
- separación por entorno.

---

# 24. Data Privacy and Security

## Controles

- anonimización;
- minimización;
- enmascaramiento;
- cifrado;
- permisos;
- retención;
- auditoría;
- separación por marca;
- datasets sintéticos;
- eliminación segura.

## Regla

Los datos sensibles de clientes, trabajadores, proveedores o empresas no deben utilizarse directamente en experimentos sin protección y autorización.

---

# 25. Integration with SBM Suite

## Flujo general

```
SBM Suite Data
      ↓
Data Pipeline
      ↓
ML Model
      ↓
Prediction API
      ↓
SBM-API / API cliente
      ↓
SBM-MANAGER / tiendas / agentes
      ↓
Human Validation
```

## Integración con `SBM-AI-ASSISTANT`

El asistente podrá:

- consultar predicciones;
- explicar resultados;
- generar resúmenes;
- detectar alertas;
- recomendar acciones;
- solicitar aprobación;
- registrar decisiones.

El LLM no debe inventar predicciones: debe consumir resultados reales de modelos o APIs.

---

# 26. Casos por dominio

## Inventario

- demanda;
- reposición;
- quiebres;
- sobrestock;
- rotación.

## Ventas

- forecasting;
- conversión;
- recomendación;
- segmentación.

## Operaciones

- anomalías;
- tiempos;
- clasificación documental;
- OCR.

## Marketing

- rendimiento;
- segmentación;
- recomendación de contenidos;
- propensión.

## Finanzas

- cash-flow forecasting;
- riesgo;
- anomalías;
- conciliación.

## Atención al cliente

- clasificación;
- prioridad;
- intención;
- satisfacción.

---

# 27. Prioridad de implementación

## Etapa 1 — Formación

- estadística;
- Scikit-learn;
- métricas;
- feature engineering;
- TensorFlow;
- PyTorch;
- notebooks;
- proyectos pequeños.

## Etapa 2 — Preparación de datos

- inventario de fuentes;
- calidad;
- anonimización;
- modelo analítico;
- pipelines.

## Etapa 3 — Primer caso SBM Suite

Caso recomendado:

- forecasting de ventas o demanda;
- baseline simple;
- modelo clásico;
- API de predicción;
- dashboard;
- documentación.

## Etapa 4 — MLOps básico

- MLflow;
- DVC;
- model registry;
- serving;
- monitoring.

## Etapa 5 — Casos avanzados

- recomendación;
- OCR;
- clasificación documental;
- anomalías;
- Deep Learning;
- visión.

---

# 28. Primer proyecto recomendado

## Demand Forecasting

### Alcance

- seleccionar un producto, material o sucursal;
- preparar histórico;
- crear baseline;
- entrenar modelos;
- comparar métricas;
- exponer predicción;
- mostrar dashboard;
- registrar experimento;
- documentar resultado.

### Evidencia de portafolio

- notebook;
- dataset anonimizado o sintético;
- pipeline;
- API;
- test;
- MLflow;
- dashboard;
- README;
- explicación de negocio.

---

# 29. Deep Learning Roadmap

1. perceptrón;
2. redes densas;
3. backpropagation;
4. regularización;
5. optimizadores;
6. CNN;
7. RNN y LSTM;
8. attention;
9. transformers;
10. transfer learning;
11. fine-tuning;
12. ONNX;
13. serving;
14. monitoring.

---

# 30. Certification and Learning Alignment

Las certificaciones y cursos deben apoyar:

- fundamentos de ML;
- Deep Learning;
- Azure AI;
- MLOps;
- data engineering;
- modelos generativos;
- evaluación;
- despliegue.

La planificación detallada se mantendrá en:

- **Certifications**;
- **Study Roadmap**.

---

# 31. Criterio de implementación

Un modelo se considera implementado cuando:

1. resuelve un problema real;
2. supera un baseline;
3. tiene métrica técnica;
4. tiene métrica de negocio;
5. es reproducible;
6. está versionado;
7. tiene pruebas;
8. está documentado;
9. tiene monitoreo;
10. tiene estrategia de rollback;
11. protege los datos;
12. puede demostrarse en el portafolio.

---

# 32. Visión final

```
Enterprise Data
      +
Machine Learning
      +
Deep Learning
      +
MLOps
      +
AI Agents
      +
Human Decisions
```

El objetivo final es que SBM Suite utilice datos históricos y operativos para predecir, recomendar, detectar y optimizar procesos, manteniendo control humano, seguridad, trazabilidad y valor empresarial medible.