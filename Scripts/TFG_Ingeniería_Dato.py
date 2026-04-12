#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 31 de marzo de 2026
# Autor: nicoverme

# En este script me conecto a la API de EDGAR para descargar los datos
# financieros de todas las empresas registradas en la SEC.
# Primero pruebo la conexión con Apple y luego descargo el dataset completo.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import requests
import pandas as pd
import time

print("Librerías cargadas correctamente")

# Defino la dirección web de la API de EDGAR para Apple Inc.
# Cada empresa tiene un número único llamado CIK.
url_apple = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"

# Inicio sesión en la API con mi email, como exige EDGAR para poder usar sus datos.
headers = {"User-Agent": "9200581@alumnos.ufv.es"}

# Me conecto a la API y descargo los datos de Apple.
respuesta = requests.get(url_apple, headers=headers)

# Compruebo que la conexión ha funcionado correctamente.
# El código 200 significa éxito. Cualquier otro número significa error.
print(f"Codigo de respuesta: {respuesta.status_code}")
print(f"Nombre de la empresa: {respuesta.json()['entityName']}")

# Convierto la respuesta de la API a un formato que Python pueda leer fácilmente.
datos_apple = respuesta.json()

# Veo qué categorías de datos financieros hay disponibles para Apple.
categorias = list(datos_apple['facts']['us-gaap'].keys())

print(f"Total de variables financieras disponibles: {len(categorias)}")
print(f"\nPrimeras 20 variables:")
for categoria in categorias[:20]:
    print(f" - {categoria}")

# Defino los 9 datos brutos que necesito para calcular los ratios financieros.
variables_que_necesito = {
    "Assets":                    "Total de activos",
    "Liabilities":               "Total de deudas",
    "StockholdersEquity":        "Patrimonio neto",
    "AssetsCurrent":             "Activos corrientes",
    "LiabilitiesCurrent":        "Deudas a corto plazo",
    "Revenues":                  "Ingresos totales",
    "OperatingIncomeLoss":       "EBIT",
    "NetIncomeLoss":             "Beneficio neto",
    "InterestExpense":           "Gastos financieros"
}

# Compruebo cuáles de estas variables están disponibles para Apple.
print("Comprobando variables para Apple:")
for variable, descripcion in variables_que_necesito.items():
    disponible = variable in categorias
    print(f" {descripcion}: {'SI' if disponible else 'NO'}")

# Creo una función que extrae los datos anuales de cualquier variable financiera.
# De esta forma no tengo que repetir el mismo código para cada variable.
def extraer_variable(datos_empresa, nombre_variable):

    # Nombres alternativos para los ingresos, ya que cada empresa
    # puede usar un nombre distinto en EDGAR para la misma variable.
    alternativas = {
        'Revenues': [
            'Revenues',
            'SalesRevenueNet',
            'RevenueFromContractWithCustomerExcludingAssessedTax',
            'SalesRevenueGoodsNet',
            'RevenuesNetOfInterestExpense'
        ]
    }

    if nombre_variable in alternativas:
        nombre_encontrado = None
        for alt in alternativas[nombre_variable]:
            if alt in datos_empresa['facts']['us-gaap']:
                nombre_encontrado = alt
                break
        if nombre_encontrado is None:
            return None
        nombre_variable = nombre_encontrado

    if nombre_variable not in datos_empresa['facts']['us-gaap']:
        return None

    valores = datos_empresa['facts']['us-gaap'][nombre_variable]['units']['USD']
    df = pd.DataFrame(valores)
    df = df[df['form'] == '10-K']
    df = df[['fy', 'val']].drop_duplicates(subset='fy', keep='last')
    df = df.rename(columns={'val': nombre_variable})

    return df

# Descargo la lista completa de empresas registradas en EDGAR.
url_empresas = "https://www.sec.gov/files/company_tickers.json"
respuesta_empresas = requests.get(url_empresas, headers=headers)
empresas = pd.DataFrame(respuesta_empresas.json()).T

print(f"Total de empresas en EDGAR: {len(empresas)}")

# Formateo el CIK con ceros a la izquierda hasta 10 dígitos.
empresas['cik_str'] = empresas['cik_str'].astype(str).str.zfill(10)

# Descargo los datos financieros de todas las empresas de EDGAR.
# Añado una pausa de 0.5 segundos entre empresa y empresa para no
# sobrecargar el servidor y evitar que me bloqueen la conexión.
dataset_completo = []
errores = 0
procesadas = 0

for index, empresa in empresas.iterrows():
    try:
        url_empresa = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{empresa['cik_str']}.json"
        respuesta_emp = requests.get(url_empresa, headers=headers)

        if respuesta_emp.status_code != 200:
            errores += 1
            continue

        datos_empresa = respuesta_emp.json()

        df_empresa = None
        for variable in variables_que_necesito.keys():
            df_var = extraer_variable(datos_empresa, variable)
            if df_var is not None:
                if df_empresa is None:
                    df_empresa = df_var
                else:
                    df_empresa = df_empresa.merge(df_var, on='fy', how='outer')

        # Solo guardo la empresa si tiene al menos 3 años de datos.
        if df_empresa is not None and len(df_empresa) >= 3:
            df_empresa['empresa'] = empresa['title']
            df_empresa['cik'] = empresa['cik_str']
            df_empresa['ticker'] = empresa['ticker']
            dataset_completo.append(df_empresa)

        procesadas += 1

        if procesadas % 100 == 0:
            print(f"Procesadas: {procesadas} | En dataset: {len(dataset_completo)} | Errores: {errores}")

        time.sleep(0.5)

    except Exception as e:
        errores += 1
        continue

print(f"\nExtracción completada.")
print(f"Empresas en el dataset: {len(dataset_completo)}")
print(f"Errores: {errores}")

# Uno todas las empresas en una sola tabla y la guardo en la carpeta de datos.
df_final = pd.concat(dataset_completo, ignore_index=True)
df_final.to_csv('Datos_CSV/dataset_edgar.csv', index=False)

print(f"Dataset guardado correctamente en Datos_CSV/dataset_edgar.csv")
print(f"Dimensiones totales: {df_final.shape}")
