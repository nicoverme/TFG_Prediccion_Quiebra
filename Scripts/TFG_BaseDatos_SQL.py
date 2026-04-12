#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 11 de abril de 2026
# Autor: nicoverme

# En este script creo la base de datos SQLite del TFG y cargo en ella
# el dataset principal y los datos de Eurostat como tablas separadas.
# Uso SQLite porque ya viene instalado con Python y no necesita configuración.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import sqlite3

print("Librerías cargadas correctamente")

# Creo la conexión a la base de datos SQLite dentro de la carpeta Base_Datos.
# Si el archivo no existe, SQLite lo crea automáticamente.
conexion = sqlite3.connect('Base_Datos/TFG_BaseDatos.db')
print("Base de datos creada correctamente: Base_Datos/TFG_BaseDatos.db")

# Cargo el dataset final completo.
df = pd.read_csv('Datos_CSV/dataset_final_completo.csv')
print(f"Dataset cargado: {df.shape[0]} filas y {df.shape[1]} columnas")

# Cargo el dataset principal en la base de datos como tabla.
# Si la tabla ya existe la reemplazo para poder ejecutar el script varias veces.
df.to_sql('empresas_financiero', conexion, if_exists='replace', index=False)
print("Tabla 'empresas_financiero' creada correctamente.")

# Cargo también los datos de Eurostat como tabla separada.
df_eurostat = pd.read_csv('Datos_CSV/eurostat_quiebras.csv')
df_eurostat.to_sql('eurostat_quiebras', conexion, if_exists='replace', index=False)
print("Tabla 'eurostat_quiebras' creada correctamente.")

# Verifico que las tablas se han creado correctamente.
cursor = conexion.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()

print(f"\nTablas en la base de datos:")
for tabla in tablas:
    print(f"  - {tabla[0]}")

# Hago una consulta de prueba para verificar que los datos están bien.
df_prueba = pd.read_sql("SELECT COUNT(*) as total_registros FROM empresas_financiero", conexion)
print(f"\nTotal de registros en la tabla principal: {df_prueba['total_registros'][0]}")

# Cierro la conexión a la base de datos.
conexion.close()
print("\nBase de datos cerrada correctamente.")
