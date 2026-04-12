#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 11 de abril de 2026
# Autor: nicoverme

# En este script limpio el dataset bruto extraído de EDGAR y calculo
# los 11 ratios financieros que usaré para predecir la quiebra empresarial.
# También añado la variable objetivo (quebró / no quebró) usando los
# registros de quiebra disponibles en la API de EDGAR.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np
import requests

print("Librerías cargadas correctamente")

# Cargo el dataset extraído de EDGAR con los nombres alternativos
# de ingresos ya incorporados en la extracción.
df = pd.read_csv('Datos_CSV/dataset_edgar.csv')

print(f"Dataset cargado correctamente.")
print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")

# Combino todas las columnas de ingresos en una sola columna llamada Revenues.
# Esto es necesario porque la extracción encontró nombres alternativos y los
# guardó como columnas separadas. Tomo el primer valor disponible por fila.
columnas_ingresos = ['Revenues', 'SalesRevenueNet',
                     'RevenueFromContractWithCustomerExcludingAssessedTax',
                     'SalesRevenueGoodsNet', 'RevenuesNetOfInterestExpense']

columnas_presentes = [c for c in columnas_ingresos if c in df.columns]
df['Revenues'] = df[columnas_presentes].bfill(axis=1).iloc[:, 0]

columnas_a_eliminar = [c for c in columnas_presentes if c != 'Revenues']
df = df.drop(columns=columnas_a_eliminar)

print(f"\nNulos en Revenues tras unificar: {round(df['Revenues'].isnull().sum() / len(df) * 100, 2)}%")

# PASO 1 - Elimino filas donde las variables más críticas están vacías.
# Sin Assets o NetIncomeLoss no puedo calcular los ratios principales.
filas_antes = len(df)
df = df.dropna(subset=['Assets', 'NetIncomeLoss'])
print(f"Filas eliminadas por nulos críticos: {filas_antes - len(df)}")

# PASO 2 - Elimino años anteriores a 1993 y posteriores a 2023.
# Me quedo con un rango temporal relevante y consistente.
df = df[(df['fy'] >= 1993) & (df['fy'] <= 2023)]
print(f"Filas tras filtrar rango temporal: {len(df)}")

# PASO 3 - Elimino bancos y aseguradoras del dataset.
# Estas empresas tienen una estructura financiera completamente diferente
# y sus ratios no son comparables con el resto de empresas.
keywords_financieras = [
    'bank', 'bancorp', 'financial', 'insurance', 'assurance',
    'trust', 'savings', 'lending', 'mortgage', 'capital'
]

mask = df['empresa'].str.lower().str.contains(
    '|'.join(keywords_financieras), na=False
)

filas_antes = len(df)
df = df[~mask]
print(f"Filas eliminadas por sector bancario/asegurador: {filas_antes - len(df)}")

# PASO 4 - Interpolación de valores nulos.
# Para cada empresa, relleno los valores nulos interpolando entre los años
# anterior y posterior disponibles.
columnas_numericas = ['Assets', 'Liabilities', 'StockholdersEquity',
                      'AssetsCurrent', 'LiabilitiesCurrent', 'Revenues',
                      'OperatingIncomeLoss', 'NetIncomeLoss', 'InterestExpense']

df = df.sort_values(['cik', 'fy'])
df[columnas_numericas] = df.groupby('cik')[columnas_numericas].transform(
    lambda x: x.interpolate(method='linear', limit_direction='both')
)

# PASO 5 - Elimino las filas que siguen teniendo nulos tras la interpolación.
filas_antes = len(df)
df = df.dropna(subset=columnas_numericas)
print(f"Filas finales tras interpolación: {len(df)}")
print(f"Empresas únicas: {df['cik'].nunique()}")

# PASO 6 - Calculo los 11 ratios financieros a partir de los 9 datos brutos.

# CATEGORÍA 1 - LIQUIDEZ
df['ratio_liquidez_corriente'] = df['AssetsCurrent'] / df['LiabilitiesCurrent']
df['ratio_liquidez_inmediata'] = (df['AssetsCurrent'] - df['AssetsCurrent'] * 0.3) / df['LiabilitiesCurrent']

# CATEGORÍA 2 - ENDEUDAMIENTO
df['ratio_endeudamiento'] = df['Liabilities'] / df['Assets']
df['ratio_autonomia_financiera'] = df['StockholdersEquity'] / df['Assets']

# CATEGORÍA 3 - RENTABILIDAD
df['ROA'] = df['NetIncomeLoss'] / df['Assets']
df['ROE'] = df['NetIncomeLoss'] / df['StockholdersEquity']
df['margen_neto'] = df['NetIncomeLoss'] / df['Revenues']

# CATEGORÍA 4 - COBERTURA DE DEUDA
df['cobertura_intereses'] = df['OperatingIncomeLoss'] / df['InterestExpense']
df['ratio_cashflow_deuda'] = df['NetIncomeLoss'] / df['Liabilities']

# CATEGORÍA 5 - EFICIENCIA
df['rotacion_activos'] = df['Revenues'] / df['Assets']

# CATEGORÍA 6 - TAMAÑO
df['log_activos'] = np.log(df['Assets'])

print("Ratios calculados correctamente.")

# Elimino los valores infinitos que pueden aparecer al dividir entre cero.
df = df.replace([np.inf, -np.inf], np.nan)

filas_antes = len(df)
df = df.dropna(subset=['ratio_liquidez_corriente', 'ratio_endeudamiento',
                        'ROA', 'ROE', 'margen_neto', 'cobertura_intereses',
                        'ratio_cashflow_deuda', 'rotacion_activos', 'log_activos'])
print(f"Filas finales tras eliminar infinitos: {len(df)}")

# PASO 7 - Añado la variable objetivo: quebró (1) o no quebró (0).
# Descargo la lista de empresas que presentaron quiebra Chapter 11 en EDGAR.
url_quiebras = "https://efts.sec.gov/LATEST/search-index?q=%22chapter+11%22&forms=8-K&dateRange=custom&startdt=1993-01-01&enddt=2023-12-31"

respuesta_quiebras = requests.get(url_quiebras, headers={'User-Agent': '9200581@alumnos.ufv.es'})
datos_quiebras = respuesta_quiebras.json()['hits']
total = datos_quiebras['total']['value']

# Pagino para obtener todos los CIKs de empresas en quiebra.
ciks_quiebra = set()
pagina = 0

while pagina * 10 < min(total, 10000):
    url_paginada = url_quiebras + f"&from={pagina * 10}&size=10"
    respuesta_pag = requests.get(url_paginada, headers={'User-Agent': '9200581@alumnos.ufv.es'})

    if respuesta_pag.status_code != 200:
        break

    hits = respuesta_pag.json()['hits']['hits']
    for hit in hits:
        fuente = hit['_source']
        if 'ciks' in fuente:
            for cik in fuente['ciks']:
                ciks_quiebra.add(str(cik).zfill(10))

    pagina += 1
    if pagina % 100 == 0:
        print(f"Páginas procesadas: {pagina} | CIKs encontrados: {len(ciks_quiebra)}")

print(f"\nTotal CIKs de empresas en quiebra: {len(ciks_quiebra)}")

# Creo la variable objetivo y corrijo el formato del CIK.
df['cik'] = df['cik'].astype(str).str.zfill(10)
df['quebro'] = df['cik'].isin(ciks_quiebra).astype(int)

print("Distribución de la variable objetivo:")
print(df['quebro'].value_counts())

# Guardo el dataset limpio en la carpeta de datos.
df.to_csv('Datos_CSV/dataset_limpio.csv', index=False)

print("\nDataset limpio guardado correctamente en Datos_CSV/dataset_limpio.csv")
print(f"Dimensiones finales: {df.shape}")
