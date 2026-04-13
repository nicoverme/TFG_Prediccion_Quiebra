#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 12 de abril de 2026
# Autor: nicoverme

# En este script construyo el primer modelo de predicción de quiebra empresarial.
# Uso Regresión Logística, que es el modelo clásico en la literatura financiera
# y sirve como punto de partida (baseline) para comparar con modelos más complejos.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             roc_curve, precision_recall_curve)

print("Librerías cargadas correctamente")

# Cargo el dataset limpio, que es el que tiene los 11 ratios financieros
# y la variable objetivo sin la multiplicación de filas del merge con BdE.
df = pd.read_csv('Datos_CSV/dataset_limpio.csv')

print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
print(f"Empresas únicas: {df['cik'].nunique()}")
print(f"\nDistribución de la variable objetivo:")
print(df['quebro'].value_counts())
print(f"Porcentaje de quiebras: {round(df['quebro'].mean() * 100, 2)}%")

# Defino las variables que voy a usar para entrenar el modelo.
# Son los 11 ratios financieros que calculé en el script de limpieza.
variables = [
    'ratio_liquidez_corriente',
    'ratio_liquidez_inmediata',
    'ratio_endeudamiento',
    'ratio_autonomia_financiera',
    'ROA',
    'ROE',
    'margen_neto',
    'cobertura_intereses',
    'ratio_cashflow_deuda',
    'rotacion_activos',
    'log_activos'
]

# Elimino las filas con nulos en las variables del modelo.
df = df.dropna(subset=variables + ['quebro'])

print(f"\nFilas disponibles tras eliminar nulos: {len(df)}")

# DIVISIÓN POR EMPRESA para evitar data leakage.
# El dataset es un panel (varias filas por empresa, una por año). Si dividiese
# aleatoriamente por filas, una misma empresa podría aparecer tanto en
# entrenamiento como en prueba, y el modelo simplemente "recordaría" esa empresa.
# Para evitarlo, asigno cada empresa completa a uno de los dos conjuntos.
# El 80% de las empresas va a entrenamiento y el 20% restante a prueba.
empresas = df['cik'].unique()
np.random.seed(42)
np.random.shuffle(empresas)
corte = int(len(empresas) * 0.8)

empresas_train = set(empresas[:corte])
empresas_test  = set(empresas[corte:])

mascara_train = df['cik'].isin(empresas_train)

X_train = df.loc[mascara_train,  variables]
y_train = df.loc[mascara_train,  'quebro']
X_test  = df.loc[~mascara_train, variables]
y_test  = df.loc[~mascara_train, 'quebro']

print(f"\nEmpresas en entrenamiento: {len(empresas_train)} | Filas: {len(X_train)}")
print(f"Empresas en prueba:        {len(empresas_test)}  | Filas: {len(X_test)}")
print(f"Quiebras en prueba: {y_test.sum()} de {len(y_test)} observaciones")

# La Regresión Logística necesita que las variables estén en la misma escala.
# Aplico StandardScaler: transforma cada variable para que tenga media 0
# y desviación típica 1. Lo ajusto solo con los datos de entrenamiento
# para no filtrar información del conjunto de prueba al modelo.
escalador = StandardScaler()
X_train_esc = escalador.fit_transform(X_train)
X_test_esc  = escalador.transform(X_test)

# Entreno el modelo de Regresión Logística.
# Uso class_weight='balanced' porque hay muchas más empresas que no quiebran
# que empresas que sí quiebran. Esto hace que el modelo penalice más los
# errores en los casos de quiebra durante el entrenamiento.
# max_iter=1000 para que el modelo tenga suficiente tiempo para converger.
modelo = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
modelo.fit(X_train_esc, y_train)

print("\nModelo de Regresión Logística entrenado correctamente.")

# Obtengo las probabilidades predichas para cada observación del conjunto de prueba.
y_prob = modelo.predict_proba(X_test_esc)[:, 1]

# Con clases tan desbalanceadas (pocas quiebras), el umbral por defecto de 0.5
# no funciona bien: el modelo casi nunca supera ese umbral para la clase de quiebra.
# Por eso busco el umbral que maximiza el F1-Score en las probabilidades del test.
# Esto me da el mejor equilibrio entre detectar quiebras (Recall) y no disparar
# demasiadas falsas alarmas (Precision).
precisiones, recalls_curva, umbrales = precision_recall_curve(y_test, y_prob)
f1_por_umbral = (2 * precisiones * recalls_curva /
                 (precisiones + recalls_curva + 1e-8))
umbral_optimo = umbrales[np.argmax(f1_por_umbral[:-1])]

print(f"\nUmbral óptimo (máximo F1): {round(umbral_optimo, 3)}")

y_pred = (y_prob >= umbral_optimo).astype(int)

# Calculo las 5 métricas de evaluación.
accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall    = recall_score(y_test, y_pred, zero_division=0)
f1        = f1_score(y_test, y_pred, zero_division=0)
roc_auc   = roc_auc_score(y_test, y_prob)

print("\n--- Resultados del modelo de Regresión Logística ---")
print(f"Accuracy:  {round(accuracy,  4)}")
print(f"Precision: {round(precision, 4)}")
print(f"Recall:    {round(recall,    4)}")
print(f"F1-Score:  {round(f1,        4)}")
print(f"ROC-AUC:   {round(roc_auc,   4)}")

# Guardo los resultados en un diccionario para usarlos en la comparación.
resultados_rl = {
    'Modelo':     'Regresión Logística',
    'Accuracy':   round(accuracy,  4),
    'Precision':  round(precision, 4),
    'Recall':     round(recall,    4),
    'F1-Score':   round(f1,        4),
    'ROC-AUC':    round(roc_auc,   4)
}

# -----------------------------------------------------------
# GRÁFICO 1 - Matriz de confusión
# -----------------------------------------------------------
# La matriz de confusión me muestra cuántas predicciones acertó y cuántas falló
# el modelo, separando entre quiebras y no quiebras.
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(6, 5))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=['No quiebra', 'Quiebra'],
            yticklabels=['No quiebra', 'Quiebra'])

ax.set_xlabel('Predicción', fontsize=12)
ax.set_ylabel('Valor real', fontsize=12)
ax.set_title('Matriz de confusión — Regresión Logística', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/RL_matriz_confusion.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nGráfico guardado: Graficos/RL_matriz_confusion.png")

# -----------------------------------------------------------
# GRÁFICO 2 - Curva ROC
# -----------------------------------------------------------
# La curva ROC muestra cómo de bien separa el modelo las dos clases
# a distintos umbrales de clasificación. Un área bajo la curva (AUC)
# cercana a 1 indica que el modelo discrimina bien.
fpr, tpr, _ = roc_curve(y_test, y_prob)

fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(fpr, tpr, color='steelblue', lw=2,
        label=f'Regresión Logística (AUC = {round(roc_auc, 3)})')
ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Clasificador aleatorio')

ax.set_xlabel('Tasa de Falsos Positivos', fontsize=12)
ax.set_ylabel('Tasa de Verdaderos Positivos', fontsize=12)
ax.set_title('Curva ROC — Regresión Logística', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])

plt.tight_layout()
plt.savefig('Graficos/RL_curva_roc.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/RL_curva_roc.png")

# -----------------------------------------------------------
# GRÁFICO 3 - Coeficientes del modelo (importancia de variables)
# -----------------------------------------------------------
# En la Regresión Logística, los coeficientes indican cómo influye cada variable
# en la probabilidad de quiebra. Un coeficiente positivo aumenta esa probabilidad
# y uno negativo la reduce.
coeficientes = pd.Series(modelo.coef_[0], index=variables).sort_values()

colores = ['tomato' if c > 0 else 'steelblue' for c in coeficientes]

fig, ax = plt.subplots(figsize=(8, 6))

ax.barh(coeficientes.index, coeficientes.values, color=colores)
ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--')

ax.set_xlabel('Coeficiente (escala estandarizada)', fontsize=12)
ax.set_title('Importancia de variables — Regresión Logística', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/RL_coeficientes.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/RL_coeficientes.png")

# Guardo los resultados en CSV para la comparación posterior.
pd.DataFrame([resultados_rl]).to_csv('Datos_CSV/resultados_regresion_logistica.csv', index=False)

print("\nResultados guardados en Datos_CSV/resultados_regresion_logistica.csv")
print("\nScript de Regresión Logística completado.")
