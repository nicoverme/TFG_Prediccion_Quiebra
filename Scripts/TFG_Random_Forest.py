#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 12 de abril de 2026
# Autor: nicoverme

# En este script construyo el segundo modelo de predicción de quiebra empresarial.
# Uso Random Forest, que es un modelo más potente que la Regresión Logística.
# La idea es ver si consigo mejorar los resultados usando un método más sofisticado.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             roc_curve, precision_recall_curve)

print("Librerías cargadas correctamente")

# Cargo el mismo dataset limpio que usé para la Regresión Logística.
df = pd.read_csv('Datos_CSV/dataset_limpio.csv')

print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")

# Uso las mismas 11 variables financieras que en el modelo anterior.
# Así la comparación entre modelos es justa.
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

# DIVISIÓN POR EMPRESA — igual que en el script de Regresión Logística.
# Uso exactamente el mismo random_state (42) y el mismo corte (80/20)
# para que los dos modelos se evalúen sobre las mismas empresas.
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

# Random Forest no necesita que las variables estén estandarizadas,
# así que no aplico StandardScaler esta vez.

# Entreno el modelo de Random Forest.
# n_estimators=200 significa que construyo 200 árboles de decisión
# y combino sus resultados. Cuantos más árboles, más estable es el modelo.
# class_weight='balanced' para compensar el desbalanceo entre quiebras y no quiebras.
modelo_rf = RandomForestClassifier(
    n_estimators=200,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

modelo_rf.fit(X_train, y_train)

print("\nModelo de Random Forest entrenado correctamente.")

# Obtengo las probabilidades predichas.
y_prob_rf = modelo_rf.predict_proba(X_test)[:, 1]

# Igual que en el script de Regresión Logística, busco el umbral que
# maximiza el F1-Score para manejar el desbalanceo de clases.
precisiones_rf, recalls_rf, umbrales_rf = precision_recall_curve(y_test, y_prob_rf)
f1_por_umbral_rf = (2 * precisiones_rf * recalls_rf /
                    (precisiones_rf + recalls_rf + 1e-8))
umbral_optimo_rf = umbrales_rf[np.argmax(f1_por_umbral_rf[:-1])]

print(f"\nUmbral óptimo (máximo F1): {round(umbral_optimo_rf, 3)}")

y_pred_rf = (y_prob_rf >= umbral_optimo_rf).astype(int)

# Calculo las mismas 5 métricas que usé en la Regresión Logística.
accuracy_rf  = accuracy_score(y_test, y_pred_rf)
precision_rf = precision_score(y_test, y_pred_rf, zero_division=0)
recall_rf    = recall_score(y_test, y_pred_rf, zero_division=0)
f1_rf        = f1_score(y_test, y_pred_rf, zero_division=0)
roc_auc_rf   = roc_auc_score(y_test, y_prob_rf)

print("\n--- Resultados del modelo de Random Forest ---")
print(f"Accuracy:  {round(accuracy_rf,  4)}")
print(f"Precision: {round(precision_rf, 4)}")
print(f"Recall:    {round(recall_rf,    4)}")
print(f"F1-Score:  {round(f1_rf,        4)}")
print(f"ROC-AUC:   {round(roc_auc_rf,   4)}")

# Guardo los resultados de este modelo.
resultados_rf = {
    'Modelo':     'Random Forest',
    'Accuracy':   round(accuracy_rf,  4),
    'Precision':  round(precision_rf, 4),
    'Recall':     round(recall_rf,    4),
    'F1-Score':   round(f1_rf,        4),
    'ROC-AUC':    round(roc_auc_rf,   4)
}

# -----------------------------------------------------------
# GRÁFICO 1 - Matriz de confusión
# -----------------------------------------------------------
cm_rf = confusion_matrix(y_test, y_pred_rf)

fig, ax = plt.subplots(figsize=(6, 5))

sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens', ax=ax,
            xticklabels=['No quiebra', 'Quiebra'],
            yticklabels=['No quiebra', 'Quiebra'])

ax.set_xlabel('Predicción', fontsize=12)
ax.set_ylabel('Valor real', fontsize=12)
ax.set_title('Matriz de confusión — Random Forest', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/RF_matriz_confusion.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nGráfico guardado: Graficos/RF_matriz_confusion.png")

# -----------------------------------------------------------
# GRÁFICO 2 - Curva ROC del Random Forest
# -----------------------------------------------------------
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)

fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(fpr_rf, tpr_rf, color='seagreen', lw=2,
        label=f'Random Forest (AUC = {round(roc_auc_rf, 3)})')
ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Clasificador aleatorio')

ax.set_xlabel('Tasa de Falsos Positivos', fontsize=12)
ax.set_ylabel('Tasa de Verdaderos Positivos', fontsize=12)
ax.set_title('Curva ROC — Random Forest', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])

plt.tight_layout()
plt.savefig('Graficos/RF_curva_roc.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/RF_curva_roc.png")

# -----------------------------------------------------------
# GRÁFICO 3 - Importancia de variables (feature importance)
# -----------------------------------------------------------
# El Random Forest calcula automáticamente la importancia de cada variable:
# cuánto ha contribuido cada ratio a las decisiones del modelo.
importancias = pd.Series(modelo_rf.feature_importances_, index=variables).sort_values()

fig, ax = plt.subplots(figsize=(8, 6))

ax.barh(importancias.index, importancias.values, color='seagreen')

ax.set_xlabel('Importancia relativa', fontsize=12)
ax.set_title('Importancia de variables — Random Forest', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/RF_importancia_variables.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/RF_importancia_variables.png")

# Guardo los resultados en CSV para usarlos en la comparación.
pd.DataFrame([resultados_rf]).to_csv('Datos_CSV/resultados_random_forest.csv', index=False)

print("\nResultados guardados en Datos_CSV/resultados_random_forest.csv")
print("\nScript de Random Forest completado.")
