import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# CONFIGURACIÓN
# ==========================================
sns.set_theme(style="whitegrid")

archivos = [
    "TEST_1_PC1_Resultados.xlsx",
    "TEST_1_PC3_Resultados.xlsx",
    "TEST_2_PC1_Resultados.xlsx",
    "TEST_2_PC3_Resultados.xlsx",
    "TEST_3_PC1_Resultados.xlsx",
    "TEST_3_PC3_Resultados.xlsx"
]

conteos_globales = []

print("Escaneando todas las hojas de los archivos Excel...")

# ==========================================
# 1. EXTRACCIÓN PROFUNDA (TODAS LAS HOJAS)
# ==========================================
for f in archivos:
    if not os.path.exists(f): 
        continue
        
    xls = pd.ExcelFile(f)
    partes = f.split('_')
    test_id = f"Test {partes[1][-1]} - {partes[2]}" # Ej: "Test 1 - PC1"
    
    # Diccionario para sumar los contadores de las 3 pruebas por archivo
    conteo_tipos = {
        'Escenario': test_id, 
        'ACK Individual': 0, 
        'ACK con Datos (Piggybacking)': 0, 
        'Delayed / Acumulativo': 0
    }
    
    for sheet in xls.sheet_names:
        if sheet.startswith("Instantaneos"):
            # Todos los de esta hoja son ACKs Puros Instantáneos
            df = pd.read_excel(xls, sheet_name=sheet)
            conteo_tipos['ACK Individual'] += len(df)
            
        elif sheet.startswith("Otros"):
            # Contamos los tipos de la columna 'Tipo_ACK'
            df = pd.read_excel(xls, sheet_name=sheet)
            if 'Tipo_ACK' in df.columns:
                vc = df['Tipo_ACK'].value_counts().to_dict()
                
                # Mapeo a nuestras 3 grandes categorías
                conteo_tipos['ACK con Datos (Piggybacking)'] += vc.get('ACK con Datos (App/Ráfaga)', 0)
                
                # Sumamos Delayed y Acumulativos en una sola categoría de retardo
                conteo_tipos['Delayed / Acumulativo'] += vc.get('Delayed ACK (Timer)', 0)
                conteo_tipos['Delayed / Acumulativo'] += vc.get('ACK Acumulativo', 0)
                
    conteos_globales.append(conteo_tipos)

# ==========================================
# 2. CÁLCULO DE PORCENTAJES
# ==========================================
df_counts = pd.DataFrame(conteos_globales)

# Calculamos el total de paquetes por escenario
df_counts['Total'] = df_counts['ACK Individual'] + df_counts['ACK con Datos (Piggybacking)'] + df_counts['Delayed / Acumulativo']

# Convertimos a porcentajes
df_counts['% Instantaneo'] = (df_counts['ACK Individual'] / df_counts['Total']) * 100
df_counts['% Piggybacking'] = (df_counts['ACK con Datos (Piggybacking)'] / df_counts['Total']) * 100
df_counts['% Otros'] = (df_counts['Delayed / Acumulativo'] / df_counts['Total']) * 100

print("Generando gráfica apilada...")

# ==========================================
# 3. GRÁFICA DE BARRAS APILADAS (100%)
# ==========================================
fig, ax = plt.subplots(figsize=(11, 6))

escenarios = df_counts['Escenario']
inst = df_counts['% Instantaneo']
piggy = df_counts['% Piggybacking']
otros = df_counts['% Otros']

# Dibujar las 3 capas
ax.bar(escenarios, inst, label='ACK Individual (Instantáneo)', color='#1f77b4') # Azul
ax.bar(escenarios, piggy, bottom=inst, label='ACK con Datos (Piggybacking)', color='#d62728') # Rojo
ax.bar(escenarios, otros, bottom=inst + piggy, label='Delayed ACK / Acumulativo', color='#ff7f0e') # Naranja

ax.set_title('5.1. Clasificación Global de Paquetes TCP', fontsize=15, fontweight='bold')
ax.set_ylabel('Proporción del Tráfico (%)')
ax.set_xlabel('Escenario de Prueba')
ax.set_ylim(0, 115) # Espacio para la leyenda
ax.legend(loc='upper center', ncol=3)

# Añadir textos centrados en cada bloque
for i, (v1, v2, v3) in enumerate(zip(inst, piggy, otros)):
    # Texto para Instantáneos
    if v1 > 5:
        ax.text(i, v1/2, f'{v1:.1f}%', ha='center', va='center', color='white', fontweight='bold')
    # Texto para Piggybacking
    if v2 > 5:
        ax.text(i, v1 + v2/2, f'{v2:.1f}%', ha='center', va='center', color='white', fontweight='bold')
    # Texto para Delayed/Acumulativos
    if v3 > 5:
        ax.text(i, v1 + v2 + v3/2, f'{v3:.1f}%', ha='center', va='center', color='black', fontweight='bold')

plt.tight_layout()
plt.savefig('Grafica_5_1Clasificacion_Total.png', dpi=300)
plt.show()

print("[OK] Gráfica guardada como 'Grafica_5_1_Clasificacion_Total.png'")