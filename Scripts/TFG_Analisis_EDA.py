#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creado el 12 de abril de 2026
# Autor: nicoverme

# En este script genero todos los gráficos necesarios para la memoria de
# Ingeniería del Dato. Los organizo en cinco secciones con un orden lógico:
# primero muestro el impacto del proceso de limpieza, luego analizo la
# variable objetivo, después estudio cada ratio individualmente, los cruzo
# con la variable de quiebra, y finalmente analizo las relaciones entre
# todas las variables a la vez.

import os
os.chdir('/Users/nicoverme/Library/CloudStorage/OneDrive-UFV/Trabajo Fin de Grado')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Librerías cargadas correctamente")

# Cargo el dataset limpio con los 11 ratios calculados y la variable objetivo.
df = pd.read_csv('Datos_CSV/dataset_limpio.csv')

print(f"Dataset cargado: {df.shape[0]} filas y {df.shape[1]} columnas")

# Defino las listas de ratios que voy a usar a lo largo del script.
ratios = ['ratio_liquidez_corriente', 'ratio_liquidez_inmediata',
          'ratio_endeudamiento', 'ratio_autonomia_financiera',
          'ROA', 'ROE', 'margen_neto', 'cobertura_intereses',
          'ratio_cashflow_deuda', 'rotacion_activos', 'log_activos']

ratios_principales = ['ratio_liquidez_corriente', 'ratio_endeudamiento',
                      'ROA', 'ROE', 'margen_neto', 'log_activos']

etiquetas_principales = ['Liquidez Corriente', 'Endeudamiento',
                         'ROA', 'ROE', 'Margen Neto', 'Log Activos']

# Separo ya el dataset en quebradas y no quebradas para usarlo en varias secciones.
df_no_quebro = df[df['quebro'] == 0]
df_quebro = df[df['quebro'] == 1]


# =============================================================================
# SECCIÓN 1 - PROCESO DE LIMPIEZA Y TRANSFORMACIÓN
# Muestro visualmente qué ocurrió con los datos durante la limpieza:
# cuántas filas se eliminaron en cada paso, cómo quedaron los nulos
# tras el tratamiento, y por qué apliqué la transformación logarítmica.
# =============================================================================

print("\n--- SECCIÓN 1: Proceso de Limpieza y Transformación ---")

# GRÁFICO 1 - Evolución del número de filas en cada paso de limpieza.
pasos = ['Dataset\noriginal', 'Tras eliminar\nnulos críticos',
         'Tras filtrar\nfechas', 'Tras eliminar\nbancos',
         'Tras interpolación\ny limpieza final']
filas = [64309, 59303, 49088, 41756, 18666]
colores_pasos = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336']

fig, ax = plt.subplots(figsize=(14, 7))
barras = ax.bar(pasos, filas, color=colores_pasos, alpha=0.85, edgecolor='white')
ax.set_title('Evolución del Dataset a lo Largo del Proceso de Limpieza', fontsize=14, fontweight='bold')
ax.set_ylabel('Número de Filas')
ax.grid(True, alpha=0.3, axis='y')

for barra, valor in zip(barras, filas):
    ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 200,
            f'{valor:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

for i in range(1, len(filas)):
    diferencia = filas[i] - filas[i-1]
    ax.text(i, filas[i] / 2, f'{diferencia:,}', ha='center', va='center',
            fontsize=9, color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/grafico_1_evolucion_limpieza.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 1 guardado.")


# GRÁFICO 2 - Porcentaje de nulos antes y después de la limpieza.
nulos_antes = {
    'Assets': 0.68, 'Liabilities': 17.92, 'StockholdersEquity': 7.11,
    'AssetsCurrent': 29.07, 'LiabilitiesCurrent': 29.34, 'Revenues': 49.11,
    'OperatingIncomeLoss': 28.23, 'NetIncomeLoss': 7.19, 'InterestExpense': 40.89
}
nulos_despues = {k: 0.0 for k in nulos_antes}

fig, ax = plt.subplots(figsize=(14, 7))
x = range(len(nulos_antes))
ancho = 0.35

barras1 = ax.bar([i - ancho/2 for i in x], nulos_antes.values(),
                  ancho, label='Antes de limpieza', color='coral', alpha=0.8)
barras2 = ax.bar([i + ancho/2 for i in x], nulos_despues.values(),
                  ancho, label='Después de limpieza', color='steelblue', alpha=0.8)

ax.set_title('Porcentaje de Valores Nulos: Antes vs Después de la Limpieza', fontsize=14, fontweight='bold')
ax.set_xlabel('Variable')
ax.set_ylabel('% de Valores Nulos')
ax.set_xticks(x)
ax.set_xticklabels(nulos_antes.keys(), rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

for barra in barras1:
    if barra.get_height() > 0:
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.5,
                f'{barra.get_height():.1f}%', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('Graficos/grafico_2_nulos_antes_despues.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 2 guardado.")


# GRÁFICO 3 - Transformación logarítmica de los activos totales.
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Transformación Logarítmica de Activos Totales: Antes vs Después', fontsize=14, fontweight='bold')

assets_clip = df['Assets'].clip(0, df['Assets'].quantile(0.95))
axes[0].hist(assets_clip, bins=50, color='coral', edgecolor='white', alpha=0.8)
axes[0].set_title('Activos Totales (escala original)')
axes[0].set_xlabel('Valor en dólares')
axes[0].set_ylabel('Frecuencia')
axes[0].grid(True, alpha=0.3)

axes[1].hist(df['log_activos'], bins=50, color='steelblue', edgecolor='white', alpha=0.8)
axes[1].set_title('Log(Activos Totales) — tras transformación')
axes[1].set_xlabel('Logaritmo del valor')
axes[1].set_ylabel('Frecuencia')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_3_transformacion_logaritmica.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 3 guardado.")


# =============================================================================
# SECCIÓN 2 - VARIABLE OBJETIVO: QUIEBRA EMPRESARIAL
# =============================================================================

print("\n--- SECCIÓN 2: Variable Objetivo ---")

# GRÁFICO 4 - Distribución de la variable objetivo.
conteo = df['quebro'].value_counts()
etiquetas_obj = ['No quebró (0)', 'Quebró (1)']
colores_obj = ['steelblue', 'coral']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Distribución de la Variable Objetivo: Quiebra Empresarial', fontsize=14, fontweight='bold')

axes[0].bar(etiquetas_obj, [conteo[0], conteo[1]], color=colores_obj, alpha=0.85, edgecolor='white')
axes[0].set_title('Número de observaciones por clase')
axes[0].set_ylabel('Número de observaciones')
axes[0].grid(True, alpha=0.3, axis='y')
for i, val in enumerate([conteo[0], conteo[1]]):
    axes[0].text(i, val + 50, f'{val:,}\n({val/len(df)*100:.1f}%)',
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

axes[1].pie([conteo[0], conteo[1]], labels=etiquetas_obj, colors=colores_obj,
            autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
axes[1].set_title('Proporción de clases')

plt.tight_layout()
plt.savefig('Graficos/grafico_4_variable_objetivo.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 4 guardado.")


# GRÁFICO 5 - Quiebras por año y tasa de quiebra anual.
quiebras_por_año = df[df['quebro'] == 1].groupby('fy').size()
empresas_por_año = df.groupby('fy').size()
tasa_quiebra = (quiebras_por_año / empresas_por_año * 100).fillna(0)

fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.suptitle('Quiebras Empresariales a lo Largo del Tiempo (1993-2023)', fontsize=14, fontweight='bold')

axes[0].bar(quiebras_por_año.index, quiebras_por_año.values, color='coral', alpha=0.85, edgecolor='white')
axes[0].set_title('Número absoluto de quiebras por año')
axes[0].set_ylabel('Número de quiebras')
axes[0].grid(True, alpha=0.3, axis='y')

max_año = quiebras_por_año.idxmax()
max_val = quiebras_por_año.max()
axes[0].annotate(f'Máximo: {max_val} ({max_año})',
                 xy=(max_año, max_val), xytext=(max_año + 2, max_val - 3),
                 arrowprops=dict(arrowstyle='->', color='black'), fontsize=10, fontweight='bold')

for año, etiq in [(2001, 'Crisis .com'), (2008, 'Crisis financiera'), (2020, 'COVID-19')]:
    if año in quiebras_por_año.index:
        axes[0].axvline(x=año, color='darkred', linestyle='--', alpha=0.5, linewidth=1.5)
        axes[0].text(año + 0.2, max_val * 0.8, etiq, fontsize=8, color='darkred', alpha=0.8)

axes[1].plot(tasa_quiebra.index, tasa_quiebra.values, color='coral', linewidth=2, marker='o', markersize=4)
axes[1].fill_between(tasa_quiebra.index, tasa_quiebra.values, alpha=0.2, color='coral')
axes[1].set_title('Tasa de quiebra anual (% sobre total de empresas del año)')
axes[1].set_xlabel('Año')
axes[1].set_ylabel('% de empresas que quebraron')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_5_quiebras_por_año.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 5 guardado.")


# =============================================================================
# SECCIÓN 3 - ANÁLISIS UNIVARIANTE DE LOS RATIOS FINANCIEROS
# =============================================================================

print("\n--- SECCIÓN 3: Análisis Univariante ---")

# GRÁFICO 6 - Distribución de los ratios financieros principales.
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Distribución de los Ratios Financieros Principales', fontsize=16, fontweight='bold')

axes[0,0].hist(df['ratio_liquidez_corriente'].clip(0, 10), bins=50, color='steelblue', edgecolor='white')
axes[0,0].set_title('Ratio de Liquidez Corriente')
axes[0,0].set_xlabel('Valor')
axes[0,0].set_ylabel('Frecuencia')
axes[0,0].grid(True, alpha=0.3)

axes[0,1].hist(df['ratio_endeudamiento'].clip(0, 2), bins=50, color='coral', edgecolor='white')
axes[0,1].set_title('Ratio de Endeudamiento')
axes[0,1].set_xlabel('Valor')
axes[0,1].grid(True, alpha=0.3)

axes[1,0].hist(df['ROA'].clip(-0.5, 0.5), bins=50, color='green', edgecolor='white')
axes[1,0].set_title('ROA (Rentabilidad sobre Activos)')
axes[1,0].set_xlabel('Valor')
axes[1,0].set_ylabel('Frecuencia')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].hist(df['margen_neto'].clip(-1, 1), bins=50, color='purple', edgecolor='white')
axes[1,1].set_title('Margen Neto')
axes[1,1].set_xlabel('Valor')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_6_distribucion_ratios.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 6 guardado.")


# GRÁFICO 7 - Boxplots para la detección de outliers.
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Detección de Valores Atípicos en los Ratios Financieros', fontsize=16, fontweight='bold')

ratios_boxplot = ['ratio_liquidez_corriente', 'ratio_endeudamiento',
                  'ROA', 'ROE', 'margen_neto', 'rotacion_activos']
titulos_box = ['Liquidez Corriente', 'Endeudamiento', 'ROA', 'ROE', 'Margen Neto', 'Rotación Activos']
colores_box = ['steelblue', 'coral', 'green', 'orange', 'purple', 'brown']

for i, (ratio, titulo, color) in enumerate(zip(ratios_boxplot, titulos_box, colores_box)):
    fila = i // 3
    col = i % 3
    datos = df[ratio].clip(df[ratio].quantile(0.01), df[ratio].quantile(0.99))
    axes[fila, col].boxplot(datos, patch_artist=True,
                            boxprops=dict(facecolor=color, alpha=0.6),
                            medianprops=dict(color='black', linewidth=2))
    axes[fila, col].set_title(titulo)
    axes[fila, col].set_ylabel('Valor')
    axes[fila, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_7_boxplots_outliers.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 7 guardado.")


# =============================================================================
# SECCIÓN 4 - ANÁLISIS BIVARIANTE: RATIOS VS QUIEBRA
# =============================================================================

print("\n--- SECCIÓN 4: Análisis Bivariante ---")

# GRÁFICO 8 - Distribución de ratios comparada entre grupos.
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Ratios Financieros: Empresas Quebradas vs No Quebradas', fontsize=16, fontweight='bold')

for i, (ratio, titulo) in enumerate(zip(ratios_principales, etiquetas_principales)):
    fila = i // 3
    col = i % 3
    lim_inf = df[ratio].quantile(0.05)
    lim_sup = df[ratio].quantile(0.95)
    axes[fila, col].hist(df_no_quebro[ratio].clip(lim_inf, lim_sup),
                         bins=40, alpha=0.6, color='steelblue', label='No quebró')
    axes[fila, col].hist(df_quebro[ratio].clip(lim_inf, lim_sup),
                         bins=40, alpha=0.6, color='red', label='Quebró')
    axes[fila, col].set_title(titulo)
    axes[fila, col].set_xlabel('Valor')
    axes[fila, col].set_ylabel('Frecuencia')
    axes[fila, col].legend()
    axes[fila, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_8_ratios_quebradas_vs_no.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 8 guardado.")


# GRÁFICO 9 - Scatter ROA vs Endeudamiento coloreado por quiebra.
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_title('ROA vs Endeudamiento según Quiebra Empresarial', fontsize=14, fontweight='bold')

df_plot = df[(df['ROA'].between(-0.5, 0.5)) & (df['ratio_endeudamiento'].between(0, 2))].copy()

ax.scatter(df_plot[df_plot['quebro'] == 0]['ratio_endeudamiento'],
           df_plot[df_plot['quebro'] == 0]['ROA'],
           alpha=0.3, color='steelblue', s=10, label='No quebró')
ax.scatter(df_plot[df_plot['quebro'] == 1]['ratio_endeudamiento'],
           df_plot[df_plot['quebro'] == 1]['ROA'],
           alpha=0.5, color='red', s=15, label='Quebró')

ax.axhline(y=0, color='black', linestyle='--', alpha=0.4, linewidth=1)
ax.axvline(x=1, color='black', linestyle='--', alpha=0.4, linewidth=1)
ax.set_xlabel('Ratio de Endeudamiento (Deuda / Activos)', fontsize=12)
ax.set_ylabel('ROA (Beneficio Neto / Activos)', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.text(0.05, 0.45, 'Alta rentabilidad\nBaja deuda', fontsize=9, color='steelblue', alpha=0.7, style='italic')
ax.text(1.5, -0.45, 'Baja rentabilidad\nAlta deuda', fontsize=9, color='red', alpha=0.7, style='italic')

plt.tight_layout()
plt.savefig('Graficos/grafico_9_scatter_ROA_endeudamiento.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 9 guardado.")


# GRÁFICO 10 - Heatmap comparativo de ratios medios por grupo.
datos_heatmap = pd.DataFrame({
    'No quebró': df[df['quebro'] == 0][ratios_principales].mean(),
    'Quebró': df[df['quebro'] == 1][ratios_principales].mean()
}, index=ratios_principales)

datos_norm = datos_heatmap.copy()
for idx in datos_norm.index:
    rango = datos_norm.loc[idx].max() - datos_norm.loc[idx].min()
    if rango != 0:
        datos_norm.loc[idx] = (datos_norm.loc[idx] - datos_norm.loc[idx].min()) / rango

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Comparativa de Ratios Medios: Quebradas vs No Quebradas', fontsize=14, fontweight='bold')

im1 = axes[0].imshow(datos_heatmap.values, cmap='RdYlGn', aspect='auto')
axes[0].set_xticks([0, 1])
axes[0].set_xticklabels(['No quebró', 'Quebró'], fontsize=11)
axes[0].set_yticks(range(len(etiquetas_principales)))
axes[0].set_yticklabels(etiquetas_principales)
axes[0].set_title('Valores medios reales por grupo')
plt.colorbar(im1, ax=axes[0])
for i in range(len(ratios_principales)):
    for j in range(2):
        axes[0].text(j, i, f'{datos_heatmap.iloc[i, j]:.3f}',
                     ha='center', va='center', fontsize=9, fontweight='bold')

im2 = axes[1].imshow(datos_norm.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
axes[1].set_xticks([0, 1])
axes[1].set_xticklabels(['No quebró', 'Quebró'], fontsize=11)
axes[1].set_yticks(range(len(etiquetas_principales)))
axes[1].set_yticklabels(etiquetas_principales)
axes[1].set_title('Diferencia relativa entre grupos (normalizado)')
plt.colorbar(im2, ax=axes[1])
for i in range(len(ratios_principales)):
    for j in range(2):
        axes[1].text(j, i, f'{datos_norm.iloc[i, j]:.2f}',
                     ha='center', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('Graficos/grafico_10_heatmap_ratios_medios.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 10 guardado.")


# =============================================================================
# SECCIÓN 5 - ANÁLISIS MULTIVARIANTE
# =============================================================================

print("\n--- SECCIÓN 5: Análisis Multivariante ---")

# GRÁFICO 11 - Matriz de correlación entre los 11 ratios financieros.
fig, ax = plt.subplots(figsize=(14, 12))
ax.set_title('Matriz de Correlación entre los 11 Ratios Financieros', fontsize=16, fontweight='bold')

correlaciones = df[ratios].corr()
im = ax.imshow(correlaciones, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax)

etiquetas = ['Liq.Corr', 'Liq.Inm', 'Endeud', 'Aut.Fin',
             'ROA', 'ROE', 'Mg.Neto', 'Cob.Int', 'CF.Deuda', 'Rot.Act', 'Log.Act']
ax.set_xticks(range(len(ratios)))
ax.set_yticks(range(len(ratios)))
ax.set_xticklabels(etiquetas, rotation=45, ha='right')
ax.set_yticklabels(etiquetas)

for i in range(len(ratios)):
    for j in range(len(ratios)):
        ax.text(j, i, f'{correlaciones.iloc[i,j]:.2f}',
                ha='center', va='center', fontsize=8,
                color='black' if abs(correlaciones.iloc[i,j]) < 0.7 else 'white')

plt.tight_layout()
plt.savefig('Graficos/grafico_11_matriz_correlacion.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 11 guardado.")


# GRÁFICO 12 - Evolución temporal de los ratios financieros (1993-2023).
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Evolución Temporal de Ratios Financieros — Mediana Anual (1993-2023)',
             fontsize=14, fontweight='bold')

evolucion = df.groupby('fy')[['ROA', 'ratio_endeudamiento',
                               'ratio_liquidez_corriente', 'margen_neto']].median()

axes[0,0].plot(evolucion.index, evolucion['ROA'], color='green', linewidth=2)
axes[0,0].set_title('ROA Mediano por Año')
axes[0,0].set_xlabel('Año')
axes[0,0].set_ylabel('ROA')
axes[0,0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(evolucion.index, evolucion['ratio_endeudamiento'], color='coral', linewidth=2)
axes[0,1].set_title('Endeudamiento Mediano por Año')
axes[0,1].set_xlabel('Año')
axes[0,1].set_ylabel('Ratio Endeudamiento')
axes[0,1].grid(True, alpha=0.3)

axes[1,0].plot(evolucion.index, evolucion['ratio_liquidez_corriente'], color='steelblue', linewidth=2)
axes[1,0].set_title('Liquidez Corriente Mediana por Año')
axes[1,0].set_xlabel('Año')
axes[1,0].set_ylabel('Ratio Liquidez')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(evolucion.index, evolucion['margen_neto'], color='purple', linewidth=2)
axes[1,1].set_title('Margen Neto Mediano por Año')
axes[1,1].set_xlabel('Año')
axes[1,1].set_ylabel('Margen Neto')
axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Graficos/grafico_12_evolucion_temporal.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 12 guardado.")


# GRÁFICO 13 - Cobertura temporal del dataset: observaciones por año.
empresas_por_año = df.groupby('fy').size()

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(empresas_por_año.index, empresas_por_año.values, color='steelblue', alpha=0.85, edgecolor='white')
ax.set_title('Cobertura Temporal del Dataset: Observaciones por Año (1993-2023)',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Año')
ax.set_ylabel('Número de observaciones')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('Graficos/grafico_13_cobertura_temporal.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico 13 guardado.")


print("\nTodos los gráficos generados correctamente.")
