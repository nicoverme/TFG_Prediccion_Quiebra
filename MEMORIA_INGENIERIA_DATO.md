<!--
FORMATO DE IMPRESIÓN:
  Fuente: Times New Roman 11 pt
  Interlineado: 1,5
  Márgenes: 2,5 cm (superior, inferior, izquierdo, derecho)
  Máximo 20 páginas de contenido (sin portada, índice ni bibliografía)
-->

---

# TRABAJO FIN DE GRADO

**Alumno:** Nicolás Vermeulen

**Título:** Predicción del riesgo de quiebra empresarial mediante técnicas de Machine Learning

**Universidad:** Universidad Francisco de Vitoria (UFV)

**Grado:** Business Analytics

**Curso académico:** 2025-2026

**Pilar:** Ingeniería del Dato

---

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

---

## ÍNDICE

1. [Introducción](#1-introducción)
2. [Diagrama de flujo ETL](#2-diagrama-de-flujo-etl)
3. [Herramientas utilizadas](#3-herramientas-utilizadas)
4. [Extracción de datos](#4-extracción-de-datos)
   - 4.1 [API EDGAR / SEC](#41-api-edgar--sec)
   - 4.2 [Eurostat](#42-eurostat)
   - 4.3 [Banco de España — SB_CBRATIOS](#43-banco-de-españa--sb_cbratios)
5. [Limpieza y Transformación](#5-limpieza-y-transformación)
   - 5.1 [Unificación de la variable de ingresos](#51-unificación-de-la-variable-de-ingresos)
   - 5.2 [Eliminación de nulos críticos](#52-eliminación-de-nulos-críticos)
   - 5.3 [Filtro temporal](#53-filtro-temporal)
   - 5.4 [Exclusión del sector financiero](#54-exclusión-del-sector-financiero)
   - 5.5 [Interpolación lineal](#55-interpolación-lineal)
   - 5.6 [Cálculo de los 11 ratios financieros](#56-cálculo-de-los-11-ratios-financieros)
   - 5.7 [Construcción de la variable objetivo](#57-construcción-de-la-variable-objetivo)
   - 5.8 [Integración de las tres fuentes](#58-integración-de-las-tres-fuentes)
6. [Carga e Infraestructura](#6-carga-e-infraestructura)
7. [Visualización y EDA](#7-visualización-y-eda)
   - 7.1 [Sección 1 — Proceso de limpieza y transformación](#71-sección-1--proceso-de-limpieza-y-transformación)
   - 7.2 [Sección 2 — Variable objetivo](#72-sección-2--variable-objetivo)
   - 7.3 [Sección 3 — Análisis univariante](#73-sección-3--análisis-univariante)
   - 7.4 [Sección 4 — Análisis bivariante](#74-sección-4--análisis-bivariante)
   - 7.5 [Sección 5 — Análisis multivariante](#75-sección-5--análisis-multivariante)
8. [Bibliografía](#8-bibliografía)

---

## 1. Introducción

La quiebra empresarial constituye uno de los fenómenos de mayor impacto económico y social en los mercados financieros. Cuando una empresa incurre en situación de insolvencia y activa los mecanismos legales de protección frente a sus acreedores —como el Chapter 11 en el ordenamiento jurídico estadounidense—, las consecuencias se extienden a empleados, proveedores, inversores y al conjunto del sistema económico. Predecir con antelación si una empresa tiene un riesgo elevado de quiebra es, por tanto, una cuestión de primera importancia tanto para las entidades financieras que conceden crédito como para los inversores que toman posiciones en renta variable. La literatura académica ha abordado este problema desde los trabajos pioneros de Altman (1968), que propuso el modelo Z-Score basado en ratios financieros, hasta los modelos modernos de aprendizaje automático, que permiten capturar relaciones no lineales entre variables y mejorar significativamente la capacidad predictiva.

Este Trabajo de Fin de Grado tiene como objetivo construir un modelo de predicción de quiebra empresarial basado en datos financieros reales extraídos directamente de fuentes institucionales. Para ello se han utilizado tres fuentes de datos complementarias: la API pública de EDGAR (Electronic Data Gathering, Analysis and Retrieval) de la Comisión de Bolsa y Valores de los Estados Unidos (SEC), que proporciona los estados financieros anuales —formulario 10-K— de más de diez mil empresas cotizadas; los datos de quiebras empresariales de Eurostat, que aportan contexto macroeconómico sobre la evolución del fenómeno en Europa; y los Cuadros de Ratios Sectoriales del Banco de España (SB_CBRATIOS), que permiten establecer referencias comparativas por sector e industria. El período de análisis abarca desde 1993 hasta 2023, proporcionando una cobertura temporal suficientemente amplia para capturar distintos ciclos económicos, incluyendo la crisis de las empresas tecnológicas de 2001, la crisis financiera global de 2008 y el impacto de la pandemia de COVID-19 en 2020.

El presente pilar de Ingeniería del Dato documenta de forma exhaustiva todo el proceso de construcción del dataset analítico: desde la extracción de datos brutos mediante llamadas a la API hasta la generación del dataset final listo para el modelado, pasando por la limpieza, la transformación, el cálculo de los indicadores financieros, la etiquetación de la variable objetivo y la carga en una base de datos relacional. El resultado de este proceso es un dataset de 18.666 observaciones empresa-año y 25 variables, que constituye la base sobre la que se construirán los modelos predictivos en los pilares posteriores del TFG.

---

## 2. Diagrama de flujo ETL

El proceso de Ingeniería del Dato se estructura como un pipeline ETL (*Extract, Transform, Load*) de seis etapas secuenciales. La representación visual completa e interactiva de este pipeline se encuentra en el archivo adjunto:

> **`DIAGRAMA_FLUJO_ETL.html`** — Diagrama interactivo donde cada bloque enlaza directamente al script o carpeta correspondiente del repositorio GitHub del proyecto.
> Repositorio: [https://github.com/nicoverme/TFG_Prediccion_Quiebra](https://github.com/nicoverme/TFG_Prediccion_Quiebra)

El diagrama muestra dos filas horizontales:

- **Fila 1:** Extracción → Limpieza → Transformación
- **Fila 2:** Carga / Base de Datos → Visualización EDA → Entregables Finales

El pipeline comienza con la extracción simultánea de las tres fuentes de datos y finaliza con el dataset analítico almacenado en una base de datos SQLite y los gráficos del análisis exploratorio exportados. Cada etapa genera uno o varios archivos intermedios que sirven como entrada a la etapa siguiente, lo que garantiza la reproducibilidad completa del proceso.

---

## 3. Herramientas utilizadas

Todo el proceso de Ingeniería del Dato se ha implementado en **Python 3**, utilizando exclusivamente librerías de código abierto. No se ha requerido ninguna licencia de software propietario.

| Librería | Versión mínima | Uso en el proyecto |
|---|---|---|
| `pandas` | 1.5 | Manipulación de DataFrames, lectura/escritura de CSV, merges, agrupaciones |
| `numpy` | 1.23 | Cálculo numérico, transformaciones logarítmicas, manejo de valores infinitos |
| `requests` | 2.28 | Llamadas HTTP a la API de EDGAR/SEC y a Eurostat |
| `sqlite3` | (estándar) | Carga del dataset en base de datos relacional SQLite |
| `matplotlib` | 3.6 | Generación de los 13 gráficos del análisis exploratorio |
| `time` | (estándar) | Control de la cadencia de peticiones a la API (pausa de 0,5 segundos) |
| `os` | (estándar) | Gestión del directorio de trabajo y listado de archivos en carpetas |

El entorno de desarrollo ha sido **Visual Studio Code** con extensión de Python, y el control de versiones se ha gestionado mediante **Git** con repositorio remoto en **GitHub**.

---

## 4. Extracción de datos

### 4.1 API EDGAR / SEC

La principal fuente de datos de este TFG es la API pública de EDGAR (*Electronic Data Gathering, Analysis and Retrieval*), el sistema de presentación de informes financieros de la SEC. Esta API proporciona acceso libre y gratuito a los estados financieros anuales —formulario **10-K**— de todas las empresas registradas en los Estados Unidos, en formato JSON estandarizado bajo el estándar XBRL (*eXtensible Business Reporting Language*).

El proceso de extracción, implementado en el script `TFG_Ingeniería_Dato.py`, se ha diseñado en dos fases. En primer lugar, se realizó una prueba de conexión utilizando como empresa de referencia **Apple Inc.** (CIK: `0000320193`), lo que permitió verificar el funcionamiento de la API y comprobar la disponibilidad de las nueve variables financieras objetivo antes de escalar la extracción al universo completo de empresas.

La API requiere identificación del agente en la cabecera HTTP (`User-Agent`), conforme a la política de uso del servidor. Cada empresa en EDGAR queda identificada por un código único denominado **CIK** (*Central Index Key*), que se formatea con diez dígitos con ceros a la izquierda. La lista completa de empresas registradas se obtiene desde el endpoint `https://www.sec.gov/files/company_tickers.json`, que devolvió más de diez mil registros en el momento de la extracción.

Para cada empresa de la lista, se descargaron las series anuales de las nueve variables financieras brutas siguientes:

| Variable EDGAR | Descripción económica |
|---|---|
| `Assets` | Total de activos |
| `Liabilities` | Total de deudas (pasivo) |
| `StockholdersEquity` | Patrimonio neto |
| `AssetsCurrent` | Activos corrientes |
| `LiabilitiesCurrent` | Pasivos corrientes (deudas a corto plazo) |
| `Revenues` | Ingresos totales |
| `OperatingIncomeLoss` | Resultado de explotación (EBIT) |
| `NetIncomeLoss` | Beneficio neto |
| `InterestExpense` | Gastos financieros (intereses) |

Un aspecto crítico durante la extracción es que **distintas empresas utilizan etiquetas XBRL diferentes para la misma variable económica**. En el caso concreto de los ingresos (`Revenues`), se identificaron cinco etiquetas alternativas: `Revenues`, `SalesRevenueNet`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueGoodsNet` y `RevenuesNetOfInterestExpense`. La función `extraer_variable()` implementada en el script gestiona automáticamente esta ambigüedad buscando las etiquetas en orden de preferencia y seleccionando la primera disponible para cada empresa.

Con objeto de cumplir con la política de uso razonable de la API del servidor de la SEC, se introdujo una **pausa de 0,5 segundos entre peticiones** consecutivas. Solo se incluyeron en el dataset aquellas empresas que disponían de datos para **un mínimo de tres ejercicios fiscales**, garantizando así la continuidad temporal mínima necesaria para el análisis de series. El resultado de esta extracción se almacenó en `Datos_CSV/dataset_edgar.csv`, con **64.309 filas** correspondientes a observaciones empresa-año.

### 4.2 Eurostat

La segunda fuente de datos es **Eurostat**, la oficina estadística de la Unión Europea. Concretamente, se utilizó el indicador *Short-term business statistics — Bankruptcy declarations* (código: `sts_rb_a_linear`), que recoge el índice anual de declaraciones de quiebra empresarial desglosado por países europeos.

El archivo CSV fue descargado manualmente desde el portal de Eurostat y procesado en el script `TFG_Eurostat_BancoEspaña.py`. El proceso de limpieza consistió en seleccionar las columnas relevantes (`geo`, `TIME_PERIOD`, `indic_bt`, `OBS_VALUE`), filtrar exclusivamente las observaciones correspondientes a quiebras (`Bankruptcy declarations`), renombrar las columnas para mayor claridad y extraer únicamente los datos correspondientes a **España** para su integración posterior con el dataset principal. El resultado se guardó en `Datos_CSV/eurostat_quiebras.csv`.

### 4.3 Banco de España — SB_CBRATIOS

La tercera fuente de datos son los **Cuadros de Ratios del Sector Privado No Financiero** elaborados por el Banco de España, disponibles en la carpeta `SB_CBRATIOS/`. Esta colección consta de **23 archivos CSV** individuales (denominados `be1507.csv` a `be1529.csv`), cada uno correspondiente a un período o corte de referencia distinto. Los archivos presentan separador de columna punto y coma (`;`) y codificación de caracteres `latin1`, características propias de los sistemas europeos.

La carga y consolidación de estos archivos se realizó mediante un bucle iterativo que lee cada fichero con la configuración correcta de separador y codificación, y los concatena en un único DataFrame con `pd.concat()`. El resultado se almacenó en `Datos_CSV/bancoespana_ratios.csv`. Esta fuente aporta datos de referencia sectorial que permiten contextualizar los ratios de las empresas individuales del dataset principal frente a los valores medios del sector.

---

## 5. Limpieza y Transformación

El proceso de limpieza y transformación, implementado en los scripts `TFG_Limpieza_Transformación.py` y `TFG_Eurostat_BancoEspaña.py`, transformó el dataset bruto de 64.309 observaciones en el dataset analítico final de 18.666 filas. A continuación se documenta cada uno de los pasos aplicados, con la cuantificación exacta de su impacto sobre el volumen de datos.

### 5.1 Unificación de la variable de ingresos

Como se ha descrito en la sección de extracción, la variable `Revenues` puede aparecer bajo cinco etiquetas XBRL distintas en el dataset bruto, generando hasta cinco columnas separadas para la misma magnitud económica. El primer paso de limpieza consiste en unificarlas en una única columna `Revenues` aplicando la función `bfill()` por filas, que toma el primer valor no nulo disponible entre las columnas de ingresos presentes. Las columnas alternativas se eliminan a continuación para simplificar el esquema del dataset.

### 5.2 Eliminación de nulos críticos

Las variables `Assets` (total de activos) y `NetIncomeLoss` (beneficio neto) son imprescindibles para el cálculo de los ratios financieros principales. Se eliminaron todas las observaciones en las que alguna de estas dos variables presentaba valor nulo. Esta operación supuso la **eliminación de 5.006 filas**, reduciendo el dataset de 64.309 a 59.303 observaciones.

El análisis del porcentaje de nulos previo a la limpieza reveló tasas especialmente elevadas en variables como `Revenues` (49,11%), `InterestExpense` (40,89%), `AssetsCurrent` (29,07%) y `LiabilitiesCurrent` (29,34%). En el caso de `Assets`, la tasa de nulos era mínima (0,68%), lo que confirma que es la variable mejor reportada por las empresas en sus formularios 10-K.

### 5.3 Filtro temporal

Se restringió el análisis al período comprendido entre **1993 y 2023**, excluyendo los datos anteriores a 1993 —cuya cobertura en EDGAR es muy limitada y poco representativa— y los ejercicios posteriores a 2023, que en el momento de la extracción podían estar incompletos. Esta operación redujo el dataset en **10.215 filas** adicionales, dejando 49.088 observaciones.

### 5.4 Exclusión del sector financiero

Las entidades financieras —bancos, aseguradoras, sociedades de capital y similares— presentan una estructura de balance radicalmente diferente a la del sector no financiero: sus pasivos son principalmente depósitos de clientes, su capital regulatorio se rige por normas de Basilea, y los ratios de endeudamiento o liquidez tienen un significado económico distinto. Incluirlas en un modelo de predicción de quiebra junto con empresas manufactureras o de servicios introduciría ruido sistemático e invalidaría la comparabilidad entre observaciones.

Se aplicó un filtro de exclusión basado en palabras clave en el nombre de la empresa, eliminando aquellas cuyo nombre contuviera alguno de los siguientes términos: `bank`, `bancorp`, `financial`, `insurance`, `assurance`, `trust`, `savings`, `lending`, `mortgage` o `capital`. Esta operación supuso la **eliminación de 7.332 observaciones**, reduciendo el dataset a 41.756 filas.

### 5.5 Interpolación lineal

Tras los filtros anteriores, el dataset presentaba todavía valores nulos en diversas variables para determinados ejercicios intermedios de empresas que sí tenían datos en años anteriores y posteriores. Para estas situaciones, se aplicó **interpolación lineal por empresa** (agrupando por CIK): para cada variable numérica, los valores nulos situados entre dos valores conocidos se estimaron mediante la recta que une dichos valores.

Este enfoque es metodológicamente correcto para la naturaleza de los datos financieros, ya que asume que la evolución de las magnitudes del balance entre dos ejercicios conocidos es aproximadamente lineal. Tras la interpolación, se eliminaron las observaciones que seguían presentando nulos en las variables numéricas principales, lo que supuso la reducción más significativa del proceso: **23.090 filas**, dejando el dataset en las **18.666 observaciones finales**.

### 5.6 Cálculo de los 11 ratios financieros

A partir de las nueve variables financieras brutas, se calcularon **once ratios financieros** agrupados en seis categorías analíticas. Los ratios financieros son indicadores adimensionales que permiten comparar empresas con independencia de su tamaño, sector geográfico o moneda de presentación, y constituyen la base estándar de la literatura académica sobre predicción de quiebra desde los trabajos de Altman (1968) y Beaver (1966).

#### Categoría 1 — Liquidez

Miden la capacidad de la empresa para hacer frente a sus obligaciones de corto plazo con sus activos más líquidos.

- **Ratio de liquidez corriente:** `AssetsCurrent / LiabilitiesCurrent`. Expresa cuántos euros de activo corriente respaldan cada euro de deuda a corto plazo. Un valor inferior a 1 indica que la empresa no dispone de suficiente activo líquido para cubrir sus deudas inmediatas.

- **Ratio de liquidez inmediata:** `(AssetsCurrent × 0,70) / LiabilitiesCurrent`. Versión más conservadora del anterior que descuenta aproximadamente el 30% del activo corriente correspondiente a existencias (inventario), el activo menos líquido dentro del circulante.

#### Categoría 2 — Endeudamiento

Miden el grado de dependencia financiera de la empresa respecto a recursos ajenos.

- **Ratio de endeudamiento:** `Liabilities / Assets`. Proporción del activo total financiada mediante deuda. Valores superiores a 0,7 suelen considerarse indicativos de riesgo financiero elevado.

- **Ratio de autonomía financiera:** `StockholdersEquity / Assets`. Proporción del activo total financiada mediante recursos propios (patrimonio neto). Complementario del ratio de endeudamiento.

#### Categoría 3 — Rentabilidad

Miden la capacidad de la empresa para generar beneficios en relación con sus recursos.

- **ROA** (*Return on Assets*): `NetIncomeLoss / Assets`. Rentabilidad generada por cada euro de activo total. Es uno de los indicadores más empleados en modelos de predicción de quiebra.

- **ROE** (*Return on Equity*): `NetIncomeLoss / StockholdersEquity`. Rentabilidad generada por cada euro de fondos propios. Especialmente relevante desde la perspectiva del accionista.

- **Margen neto:** `NetIncomeLoss / Revenues`. Porcentaje de los ingresos que se convierte en beneficio neto tras deducir todos los costes y gastos. Mide la eficiencia global de la cuenta de resultados.

#### Categoría 4 — Cobertura de deuda

Miden la capacidad de la empresa para hacer frente a sus obligaciones financieras con los flujos generados por la actividad.

- **Ratio de cobertura de intereses:** `OperatingIncomeLoss / InterestExpense`. Número de veces que el resultado de explotación (EBIT) cubre los gastos financieros. Un valor inferior a 1 indica que la empresa no genera suficiente resultado operativo para pagar sus intereses.

- **Ratio de cashflow sobre deuda:** `NetIncomeLoss / Liabilities`. Aproximación al flujo de caja generado por cada euro de deuda total. Indicador de sostenibilidad del endeudamiento a largo plazo.

#### Categoría 5 — Eficiencia

Mide la intensidad con la que la empresa utiliza sus activos para generar ventas.

- **Rotación de activos:** `Revenues / Assets`. Euros de ingresos generados por cada euro de activo total. Valores elevados indican un uso eficiente de los recursos productivos.

#### Categoría 6 — Tamaño

Controla el efecto del tamaño empresarial en el modelo.

- **Logaritmo de activos totales:** `log(Assets)`. Transformación logarítmica natural del activo total. Se aplica para corregir la fuerte asimetría positiva de la distribución de activos, que oscila desde miles hasta billones de dólares. Tras la transformación, la variable sigue una distribución aproximadamente normal.

Tras el cálculo de los once ratios, se sustituyeron los valores infinitos —que pueden aparecer al dividir entre cero, por ejemplo en el ratio de cobertura de intereses cuando los gastos financieros son nulos— por valores nulos, eliminándose a continuación las observaciones que los contenían.

### 5.7 Construcción de la variable objetivo

La variable objetivo binaria `quebro` indica si una empresa ha presentado una declaración de quiebra bajo el **Chapter 11** del código de quiebras de los Estados Unidos en algún momento de su historia registrada en EDGAR.

La identificación de las empresas en quiebra se realizó consultando el motor de búsqueda de texto completo de EDGAR (*EFTS — EDGAR Full Text Search*), que indexa el contenido de los formularios 8-K (comunicaciones de hechos relevantes). Se realizó una búsqueda de todos los formularios 8-K que contuvieran la expresión literal `"chapter 11"` en el período 1993-2023, paginando los resultados hasta obtener el conjunto máximo disponible (10.000 registros). Para cada registro encontrado se extrajeron los CIKs de las empresas implicadas, construyendo así el conjunto de empresas que en algún momento presentaron quiebra.

Finalmente, se creó la variable `quebro` asignando el valor **1** a las observaciones cuyo CIK formaba parte de dicho conjunto y **0** al resto. La variable es de naturaleza binaria y constituirá la variable dependiente de los modelos de clasificación que se desarrollarán en los pilares posteriores del TFG.

### 5.8 Integración de las tres fuentes

Una vez procesados por separado los datos de EDGAR (limpiados y transformados), Eurostat y Banco de España, se procedió a su integración en el dataset final. La unión con los datos de Eurostat se realizó mediante un `merge` sobre la columna del año fiscal (`fy`), incorporando el índice anual de quiebras empresariales en España como variable de contexto macroeconómico. Este dataset final, con **18.666 filas y 25 columnas**, se almacenó en `Datos_CSV/dataset_final_completo.csv`.

---

## 6. Carga e Infraestructura

El dataset final se ha cargado en una base de datos relacional **SQLite** mediante el script `TFG_BaseDatos_SQL.py`. La elección de SQLite responde a criterios de simplicidad y portabilidad: al estar integrado en la librería estándar de Python (`sqlite3`), no requiere la instalación ni configuración de ningún servidor de base de datos externo, y el archivo de base de datos resultante (`TFG_BaseDatos.db`) es un único fichero autocontenido y fácilmente transportable.

La base de datos contiene **dos tablas**:

| Tabla | Contenido | Origen |
|---|---|---|
| `empresas_financiero` | Dataset principal con los 11 ratios, la variable objetivo y las variables originales | `dataset_final_completo.csv` |
| `eurostat_quiebras` | Índice anual de quiebras por país europeo (Eurostat) | `eurostat_quiebras.csv` |

El script implementa la carga con la opción `if_exists='replace'`, lo que permite ejecutarlo tantas veces como sea necesario sin duplicar datos. Tras la carga, se realiza una **consulta de verificación** (`SELECT COUNT(*) FROM empresas_financiero`) para confirmar que el número de registros almacenados en la base de datos coincide con el del archivo CSV de origen, garantizando así la integridad del proceso de carga.

La base de datos SQLite facilita la realización de consultas analíticas mediante SQL en las fases posteriores del proyecto, así como la integración con herramientas de visualización y con los entornos de modelado estadístico.

---

## 7. Visualización y EDA

El análisis exploratorio de datos (EDA, *Exploratory Data Analysis*) se ha realizado en el script `TFG_Analisis_EDA.py` y se estructura en **cinco secciones temáticas** que generan un total de **13 gráficos** exportados en formato PNG a alta resolución (150 dpi) en la carpeta `Graficos/`.

### 7.1 Sección 1 — Proceso de limpieza y transformación

**Gráfico 1 — Evolución del dataset durante la limpieza** (`grafico_1_evolucion_limpieza.png`)

Gráfico de barras que muestra el número de filas del dataset en cada etapa del proceso de limpieza. Cada barra corresponde a un paso específico, con la diferencia respecto al paso anterior anotada en el interior de la barra. El gráfico permite visualizar de forma intuitiva el impacto de cada decisión metodológica sobre el volumen final de datos. Los cinco hitos son: dataset original (64.309 filas), tras eliminar nulos críticos (59.303), tras filtrar fechas (49.088), tras eliminar el sector bancario (41.756) y tras la interpolación y limpieza final (18.666).

**Gráfico 2 — Valores nulos antes y después de la limpieza** (`grafico_2_nulos_antes_despues.png`)

Gráfico de barras agrupadas que compara, para cada una de las nueve variables financieras brutas, el porcentaje de valores nulos antes y después del proceso de limpieza. Antes de la limpieza destacan los altos porcentajes de `Revenues` (49,11%), `InterestExpense` (40,89%) y `LiabilitiesCurrent` (29,34%), que reflejan la heterogeneidad en los criterios de presentación de información financiera por parte de las empresas en sus formularios EDGAR. Después de la limpieza, el porcentaje de nulos en todas las variables es **0,0%**.

**Gráfico 3 — Transformación logarítmica de los activos** (`grafico_3_transformacion_logaritmica.png`)

Panel de dos histogramas que ilustra la necesidad y el efecto de la transformación logarítmica aplicada a la variable `Assets`. El histograma izquierdo muestra la distribución original, que presenta una asimetría positiva extrema: la mayoría de empresas tienen activos modestos, pero un pequeño número de grandes corporaciones genera una cola derecha muy larga. El histograma derecho muestra la distribución de `log(Assets)`, que se aproxima a una distribución normal y resulta mucho más adecuada para su uso como predictor en modelos estadísticos.

### 7.2 Sección 2 — Variable objetivo

**Gráfico 4 — Distribución de la variable objetivo** (`grafico_4_variable_objetivo.png`)

Panel de dos gráficos —barras y diagrama de sectores— que muestra la distribución de las observaciones entre empresas que quebraron (clase 1) y empresas que no quebraron (clase 0). El dataset presenta un marcado **desbalanceo de clases**, con una proporción significativamente mayor de observaciones de clase 0, lo que es habitual en problemas de detección de eventos raros como la quiebra empresarial. Este desbalanceo deberá ser tenido en cuenta en el pilar de Modelado, aplicando técnicas de sobremuestreo (SMOTE), infra-muestreo o ponderación de clases según proceda.

**Gráfico 5 — Quiebras por año y tasa de quiebra anual** (`grafico_5_quiebras_por_año.png`)

Panel de dos gráficos que analiza la distribución temporal de las quiebras. El gráfico superior muestra el número absoluto de quiebras por año, con líneas verticales discontinuas que señalan los tres grandes choques económicos del período: la crisis de las empresas tecnológicas (2001), la crisis financiera global (2008) y la pandemia de COVID-19 (2020). El gráfico inferior muestra la **tasa de quiebra anual** —número de quiebras dividido por el total de empresas activas en cada año— como serie temporal, lo que elimina el efecto del crecimiento del número de empresas en el dataset a lo largo del tiempo y permite comparar la intensidad del fenómeno entre distintos períodos.

### 7.3 Sección 3 — Análisis univariante

**Gráfico 6 — Distribución de los ratios financieros principales** (`grafico_6_distribucion_ratios.png`)

Panel de cuatro histogramas que muestra la distribución de los ratios de liquidez corriente, endeudamiento, ROA y margen neto sobre el conjunto completo del dataset. Los histogramas se representan con recorte de valores extremos (*winsorización*) en los percentiles apropiados para mejorar la legibilidad. Se observa que el ratio de liquidez corriente presenta una distribución con cola derecha, mientras que el ROA y el margen neto presentan distribuciones aproximadamente simétricas en torno a cero, con ligera concentración en valores positivos.

**Gráfico 7 — Detección de valores atípicos** (`grafico_7_boxplots_outliers.png`)

Matriz de seis diagramas de caja (*boxplots*) que muestra la presencia de valores atípicos en los ratios de liquidez corriente, endeudamiento, ROA, ROE, margen neto y rotación de activos. Los datos se representan recortados entre los percentiles 1 y 99 para mantener la escala legible. Los boxplots revelan que todos los ratios presentan valores atípicos relevantes en ambas colas, lo que justifica la aplicación de técnicas de tratamiento de outliers en la fase de modelado.

### 7.4 Sección 4 — Análisis bivariante

**Gráfico 8 — Ratios financieros por grupo de quiebra** (`grafico_8_ratios_quebradas_vs_no.png`)

Matriz de seis histogramas superpuestos que compara la distribución de los seis ratios principales entre empresas que quebraron (clase 1, en rojo) y empresas que no quebraron (clase 0, en azul). Este gráfico es clave para evaluar el **poder discriminante** de cada ratio. Se observa que las empresas quebradas presentan, en media, menores valores de ROA, margen neto y autonomía financiera, y mayores valores de endeudamiento, lo que es consistente con la teoría económica y con los hallazgos de la literatura previa.

**Gráfico 9 — Dispersión ROA vs Endeudamiento** (`grafico_9_scatter_ROA_endeudamiento.png`)

Diagrama de dispersión que enfrenta el ROA (eje Y) contra el ratio de endeudamiento (eje X), coloreando cada punto según la clase de quiebra. Se representan únicamente las observaciones dentro del rango intercuartílico para evitar la distorsión por valores extremos. El gráfico muestra una separación estadística entre grupos: las empresas quebradas tienden a concentrarse en la zona de **alta deuda y baja rentabilidad** (cuadrante inferior derecho), mientras que las empresas sanas predominan en la zona de **baja deuda y alta rentabilidad** (cuadrante superior izquierdo). Las líneas discontinuas en ROA = 0 y Endeudamiento = 1 actúan como referencias visuales.

**Gráfico 10 — Heatmap comparativo de ratios medios** (`grafico_10_heatmap_ratios_medios.png`)

Panel de dos mapas de calor (*heatmaps*) que sintetiza las diferencias entre grupos. El mapa izquierdo muestra los **valores medios reales** de los seis ratios principales para cada clase, con los valores numéricos anotados en cada celda. El mapa derecho muestra los mismos datos **normalizados** entre 0 y 1 dentro de cada ratio, lo que permite comparar visualmente la magnitud relativa de las diferencias entre grupos independientemente de la escala de cada ratio.

### 7.5 Sección 5 — Análisis multivariante

**Gráfico 11 — Matriz de correlación** (`grafico_11_matriz_correlacion.png`)

Mapa de calor de la matriz de correlación de Pearson entre los once ratios financieros. Se emplea la escala de colores `coolwarm` (rojo para correlaciones positivas fuertes, azul para correlaciones negativas fuertes). El gráfico permite identificar pares de ratios con alta multicolinealidad que podrían requerir tratamiento específico en el modelado —como la reducción de dimensionalidad mediante PCA— así como grupos de ratios que capturan dimensiones financieras independientes.

**Gráfico 12 — Evolución temporal de los ratios** (`grafico_12_evolucion_temporal.png`)

Panel de cuatro series temporales que muestra la **mediana anual** de los ratios de ROA, endeudamiento, liquidez corriente y margen neto para el período 1993-2023. El uso de la mediana en lugar de la media evita la distorsión causada por valores extremos. Las series permiten detectar tendencias estructurales y el impacto de los ciclos económicos sobre la salud financiera media del universo de empresas analizado.

**Gráfico 13 — Cobertura temporal del dataset** (`grafico_13_cobertura_temporal.png`)

Gráfico de barras que muestra el número de observaciones empresa-año disponibles para cada ejercicio fiscal entre 1993 y 2023. El gráfico verifica que el dataset tiene una cobertura temporal razonablemente uniforme a lo largo del período de análisis, con un crecimiento paulatino en los primeros años —a medida que más empresas se incorporan a EDGAR— y cierta estabilización a partir de mediados de los años 2000.

---

## 8. Bibliografía

Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. *The Journal of Finance*, 23(4), 589-609. https://doi.org/10.1111/j.1540-6261.1968.tb00843.x

Beaver, W. H. (1966). Financial ratios as predictors of failure. *Journal of Accounting Research*, 4, 71-111. https://doi.org/10.2307/2490171

Ohlson, J. A. (1980). Financial ratios and the probabilistic prediction of bankruptcy. *Journal of Accounting Research*, 18(1), 109-131. https://doi.org/10.2307/2490395

Shumway, T. (2001). Forecasting bankruptcy more accurately: A simple hazard model. *The Journal of Business*, 74(1), 101-124. https://doi.org/10.1086/209665

U.S. Securities and Exchange Commission. (2024). *EDGAR Full-Text Search API — Developer Documentation*. https://efts.sec.gov/LATEST/search-index

U.S. Securities and Exchange Commission. (2024). *XBRL Financial Data API*. https://data.sec.gov/api/xbrl/

Eurostat. (2024). *Short-term business statistics — Bankruptcies (sts_rb_a)*. European Commission. https://ec.europa.eu/eurostat/databrowser/view/sts_rb_a

Banco de España. (2024). *Central de Balances — Cuadros de ratios del sector privado no financiero (SB_CBRATIOS)*. https://www.bde.es/bde/es/areas/cenbal/

McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 445, 51-56.

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90-95. https://doi.org/10.1109/MCSE.2007.55
