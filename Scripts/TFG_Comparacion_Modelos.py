#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 12 de abril de 2026
# Autor: nicoverme

# En este script comparo los dos modelos que he construido: Regresión Logística
# y Random Forest. Cargo los resultados que guardé en los scripts anteriores
# y genero gráficos comparativos para poder ver cuál funciona mejor.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_curve, roc_auc_score, confusion_matrix,
                             precision_recall_curve)

print("Librerías cargadas correctamente")

# Cargo los resultados guardados por cada script de modelo.
res_rl = pd.read_csv('Datos_CSV/resultados_regresion_logistica.csv')
res_rf = pd.read_csv('Datos_CSV/resultados_random_forest.csv')

comparacion = pd.concat([res_rl, res_rf], ignore_index=True)

print("\nComparación de métricas:")
print(comparacion.to_string(index=False))

# -----------------------------------------------------------
# GRÁFICO 1 - Barras comparativas de las 5 métricas
# -----------------------------------------------------------
metricas = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']

valores_rl = comparacion.loc[comparacion['Modelo'] == 'Regresión Logística', metricas].values[0]
valores_rf = comparacion.loc[comparacion['Modelo'] == 'Random Forest', metricas].values[0]

x = np.arange(len(metricas))
ancho = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

barras_rl = ax.bar(x - ancho/2, valores_rl, ancho, label='Regresión Logística', color='steelblue')
barras_rf = ax.bar(x + ancho/2, valores_rf, ancho, label='Random Forest',       color='seagreen')

# Añado el valor encima de cada barra para que se lea bien.
for barra in barras_rl:
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.005,
            f'{barra.get_height():.3f}',
            ha='center', va='bottom', fontsize=9)

for barra in barras_rf:
    ax.text(barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.005,
            f'{barra.get_height():.3f}',
            ha='center', va='bottom', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(metricas, fontsize=11)
ax.set_ylabel('Valor de la métrica', fontsize=12)
ax.set_ylim(0, 1.15)
ax.set_title('Comparación de métricas entre modelos', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig('Graficos/Comparacion_metricas.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nGráfico guardado: Graficos/Comparacion_metricas.png")

# -----------------------------------------------------------
# Para los gráficos 2 y 3 necesito reentrenar ambos modelos
# usando exactamente la misma división que en los scripts anteriores.
# -----------------------------------------------------------
df = pd.read_csv('Datos_CSV/dataset_limpio.csv')

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

df = df.dropna(subset=variables + ['quebro'])

# Reproduzco la misma división por empresa que usé en los scripts de cada modelo.
empresas = df['cik'].unique()
np.random.seed(42)
np.random.shuffle(empresas)
corte = int(len(empresas) * 0.8)

empresas_train = set(empresas[:corte])
mascara_train  = df['cik'].isin(empresas_train)

X_train = df.loc[mascara_train,  variables]
y_train = df.loc[mascara_train,  'quebro']
X_test  = df.loc[~mascara_train, variables]
y_test  = df.loc[~mascara_train, 'quebro']

# Regresión Logística (necesita escalado).
escalador    = StandardScaler()
X_train_esc  = escalador.fit_transform(X_train)
X_test_esc   = escalador.transform(X_test)

rl = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
rl.fit(X_train_esc, y_train)
prob_rl = rl.predict_proba(X_test_esc)[:, 1]

# Umbral óptimo para Regresión Logística.
prec_rl, rec_rl, thr_rl = precision_recall_curve(y_test, prob_rl)
f1_rl = 2 * prec_rl * rec_rl / (prec_rl + rec_rl + 1e-8)
umbral_rl = thr_rl[np.argmax(f1_rl[:-1])]
pred_rl = (prob_rl >= umbral_rl).astype(int)

# Random Forest (no necesita escalado).
rf = RandomForestClassifier(n_estimators=200, class_weight='balanced',
                            random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
prob_rf = rf.predict_proba(X_test)[:, 1]

# Umbral óptimo para Random Forest.
prec_rf, rec_rf, thr_rf = precision_recall_curve(y_test, prob_rf)
f1_rf_arr = 2 * prec_rf * rec_rf / (prec_rf + rec_rf + 1e-8)
umbral_rf = thr_rf[np.argmax(f1_rf_arr[:-1])]
pred_rf = (prob_rf >= umbral_rf).astype(int)

# -----------------------------------------------------------
# GRÁFICO 2 - Curvas ROC comparadas en un solo gráfico
# -----------------------------------------------------------
fpr_rl, tpr_rl, _ = roc_curve(y_test, prob_rl)
fpr_rf, tpr_rf, _ = roc_curve(y_test, prob_rf)

auc_rl = roc_auc_score(y_test, prob_rl)
auc_rf = roc_auc_score(y_test, prob_rf)

fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(fpr_rl, tpr_rl, color='steelblue', lw=2,
        label=f'Regresión Logística (AUC = {round(auc_rl, 3)})')
ax.plot(fpr_rf, tpr_rf, color='seagreen',  lw=2,
        label=f'Random Forest       (AUC = {round(auc_rf, 3)})')
ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Clasificador aleatorio')

ax.set_xlabel('Tasa de Falsos Positivos', fontsize=12)
ax.set_ylabel('Tasa de Verdaderos Positivos', fontsize=12)
ax.set_title('Curvas ROC — Comparación de modelos', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])

plt.tight_layout()
plt.savefig('Graficos/Comparacion_curvas_roc.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/Comparacion_curvas_roc.png")

# -----------------------------------------------------------
# GRÁFICO 3 - Matrices de confusión lado a lado
# -----------------------------------------------------------
cm_rl = confusion_matrix(y_test, pred_rl)
cm_rf = confusion_matrix(y_test, pred_rf)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.heatmap(cm_rl, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['No quiebra', 'Quiebra'],
            yticklabels=['No quiebra', 'Quiebra'])
axes[0].set_xlabel('Predicción', fontsize=11)
axes[0].set_ylabel('Valor real', fontsize=11)
axes[0].set_title('Regresión Logística', fontsize=12, fontweight='bold')

sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens', ax=axes[1],
            xticklabels=['No quiebra', 'Quiebra'],
            yticklabels=['No quiebra', 'Quiebra'])
axes[1].set_xlabel('Predicción', fontsize=11)
axes[1].set_ylabel('Valor real', fontsize=11)
axes[1].set_title('Random Forest', fontsize=12, fontweight='bold')

fig.suptitle('Matrices de confusión — Comparación de modelos',
             fontsize=13, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('Graficos/Comparacion_matrices_confusion.png', dpi=150, bbox_inches='tight')
plt.close()

print("Gráfico guardado: Graficos/Comparacion_matrices_confusion.png")

# Guardo la tabla de comparación completa en CSV.
comparacion.to_csv('Datos_CSV/comparacion_modelos.csv', index=False)
print("\nTabla comparativa guardada en Datos_CSV/comparacion_modelos.csv")

print("\nScript de comparación completado.")
