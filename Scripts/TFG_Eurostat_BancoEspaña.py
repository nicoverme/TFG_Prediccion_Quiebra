#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 11 de abril de 2026
# Autor: nicoverme

# En este script cargo y proceso los datos de Eurostat y del Banco de España,
# que son las dos fuentes externas que complementan los datos de EDGAR.
# Al final uno las tres fuentes en el dataset final completo.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np

print("Librerías cargadas correctamente")

# Cargo el archivo de Eurostat descargado manualmente.
# Contiene el índice de quiebras empresariales anuales por país europeo.
df_eurostat = pd.read_csv('Datos_CSV/sts_rb_a_linear.csv')

print("Datos de Eurostat cargados correctamente.")
print(f"Filas: {df_eurostat.shape[0]}")
print(f"Columnas: {df_eurostat.shape[1]}")

# Selecciono solo las columnas que me interesan de Eurostat.
df_eurostat = df_eurostat[['geo', 'TIME_PERIOD', 'indic_bt', 'OBS_VALUE']]

# Filtro solo los datos de quiebras (bankruptcies), no registros.
df_eurostat = df_eurostat[df_eurostat['indic_bt'] == 'Bankruptcy declarations']

# Renombro las columnas para que sean más claras.
df_eurostat = df_eurostat.rename(columns={
    'geo': 'pais',
    'TIME_PERIOD': 'año',
    'OBS_VALUE': 'indice_quiebras_eurostat'
})

df_eurostat = df_eurostat.drop(columns=['indic_bt'])

print(f"Países disponibles: {df_eurostat['pais'].unique()}")

# Guardo los datos de Eurostat limpios en la carpeta de datos.
df_eurostat.to_csv('Datos_CSV/eurostat_quiebras.csv', index=False)
print("Datos de Eurostat guardados en Datos_CSV/eurostat_quiebras.csv")

# Cargo los datos del Banco de España.
# Los datos vienen en múltiples archivos CSV dentro de la carpeta SB_CBRATIOS.
import os as os_files

carpeta_bde = 'SB_CBRATIOS'
archivos = [f for f in os_files.listdir(carpeta_bde) if f.endswith('.csv')]

print(f"\nArchivos del Banco de España encontrados: {len(archivos)}")

lista_dfs = []
for archivo in archivos:
    try:
        df_temp = pd.read_csv(f"{carpeta_bde}/{archivo}", sep=';', encoding='latin1')
        lista_dfs.append(df_temp)
    except:
        continue

df_bde = pd.concat(lista_dfs, ignore_index=True)

print(f"Total de filas del Banco de España: {len(df_bde)}")

# Guardo los datos del Banco de España en la carpeta de datos.
df_bde.to_csv('Datos_CSV/bancoespana_ratios.csv', index=False)
print("Datos del Banco de España guardados en Datos_CSV/bancoespana_ratios.csv")

# Uno las 3 fuentes en el dataset final.
# Cargo el dataset limpio de EDGAR.
df_principal = pd.read_csv('Datos_CSV/dataset_limpio.csv')

# Añado el índice de quiebras de Eurostat para España como contexto.
df_eurostat_españa = df_eurostat[df_eurostat['pais'] == 'Spain'].copy()
df_eurostat_españa = df_eurostat_españa.rename(columns={'año': 'fy'})

df_final = df_principal.merge(df_eurostat_españa[['fy', 'indice_quiebras_eurostat']],
                               on='fy', how='left')

print(f"\nDataset final con las 3 fuentes:")
print(f"Filas: {df_final.shape[0]}")
print(f"Columnas: {df_final.shape[1]}")

# Guardo el dataset final completo en la carpeta de datos.
df_final.to_csv('Datos_CSV/dataset_final_completo.csv', index=False)
print("\nDataset final completo guardado en Datos_CSV/dataset_final_completo.csv")
