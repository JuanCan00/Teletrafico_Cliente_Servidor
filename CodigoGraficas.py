import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================
# Estilo visual de las gráficas
sns.set_theme(style="whitegrid")

# Lista exacta de los archivos Excel
archivos = [
    "TEST_1_PC1_Resultados.xlsx",
    "TEST_1_PC3_Resultados.xlsx",
    "TEST_2_PC1_Resultados.xlsx",
    "TEST_2_PC3_Resultados.xlsx",
    "TEST_3_PC1_Resultados.xlsx",
    "TEST_3_PC3_Resultados.xlsx"
]

datos_completos = []

print("Cargando y procesando archivos Excel...")

# ==========================================
# 1. LECTURA Y CONSOLIDACIÓN DE DATOS
# ==========================================
for archivo in archivos:
    if os.path.exists(archivo):
        # Leemos únicamente la hoja "Resumen_Comparativo"
        df = pd.read_excel(archivo, sheet_name="Resumen_Comparativo")
        
        # Extraemos el número de test y PC desde el nombre del archivo
        partes_nombre = archivo.split('_')
        num_test = partes_nombre[1] # Ej: "1"
        num_pc = partes_nombre[2]   # Ej: "PC1"
        
        # Insertamos columnas identificadoras para facilitar la agrupación
        df.insert(0, 'PC', num_pc)
        df.insert(0, 'Test', f"Test {num_test[-1]}") # Aseguramos capturar solo el número
        
        datos_completos.append(df)
    else:
        print(f"[!] Advertencia: No se encontró el archivo {archivo}")

if not datos_completos:
    print("No se cargaron datos. Verifica que los archivos Excel estén en la misma carpeta que este script.")
else:
    # Unimos todos los dataframes en uno solo
    df_consolidado = pd.concat(datos_completos, ignore_index=True)
    
    # ==========================================
    # 2. LIMPIEZA Y PREPARACIÓN DE VARIABLES
    # ==========================================
    # Convertimos el porcentaje (texto con símbolo %) a número flotante
    df_consolidado['Porcentaje_Instantaneo_num'] = df_consolidado['Porcentaje_Instantaneo'].str.rstrip('%').astype(float)
    
    # Convertimos los tiempos de Segundos a Milisegundos para las gráficas
    df_consolidado['Viaje_Red_Neto_ms'] = df_consolidado['Viaje_Red_Neto_s'] * 1000
    df_consolidado['Respuesta_SV_ms'] = df_consolidado['Respuesta_SV_s'] * 1000
    df_consolidado['Tiempo_C_S_ms'] = df_consolidado['Tiempo_C_S_s'] * 1000
    df_consolidado['Tiempo_S_C_ms'] = df_consolidado['Tiempo_S_C_s'] * 1000
    
    # ==========================================
    # 3. AGRUPACIÓN (Promedios por Test y PC)
    # ==========================================
    # Agrupamos las 3 pruebas de cada Test para obtener un solo promedio general
    df_agrupado = df_consolidado.groupby(['Test', 'PC']).agg({
        'Total_Segmentos': 'mean', # Columna original del Excel
        'Muestras_Instantaneas': 'mean',
        'Porcentaje_Instantaneo_num': 'mean',
        'Viaje_Red_Neto_ms': 'mean',
        'Respuesta_SV_ms': 'mean',
        'Tiempo_C_S_ms': 'mean',
        'Tiempo_S_C_ms': 'mean'
    }).reset_index()
    
    # Renombramos internamente la columna a Paquetes para evitar confusiones
    df_agrupado.rename(columns={'Total_Segmentos': 'Total_Paquetes'}, inplace=True)
    
    # Creamos una etiqueta unificada para el Eje X (Ej: "Test 1 - PC1")
    df_agrupado['Escenario'] = df_agrupado['Test'] + " - " + df_agrupado['PC']
    
    # Calculamos el porcentaje restante (Piggybacking)
    df_agrupado['Piggybacked_num'] = 100 - df_agrupado['Porcentaje_Instantaneo_num']

    print("Generando gráficas...")

    # ==========================================
    # GRÁFICA 5.1: Total de Paquetes TCP
    # ==========================================
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df_agrupado, x='Escenario', y='Total_Paquetes', palette='Blues_d')
    plt.title('5.1. Promedio de Paquetes TCP Capturados por Escenario', fontsize=14, fontweight='bold')
    plt.ylabel('Cantidad de Paquetes')
    plt.xlabel('Escenario de Prueba')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('Grafica_5_1_Clasificacion.png', dpi=300)
    plt.close()

    # ==========================================
    # GRÁFICA 5.2: Tiempo de Red Neto
    # ==========================================
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df_agrupado, x='Escenario', y='Viaje_Red_Neto_ms', palette='Greens_d')
    plt.title('5.2. Tiempo de Red Neto (Ida y Vuelta) por Escenario', fontsize=14, fontweight='bold')
    plt.ylabel('Tiempo (ms)')
    plt.xlabel('Escenario de Prueba')
    plt.ylim(0, 1.0)
    
    for index, row in df_agrupado.iterrows():
        plt.text(index, row.Viaje_Red_Neto_ms + 0.02, f'{row.Viaje_Red_Neto_ms:.2f} ms', color='black', ha="center")
        
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('Grafica_5_2_TiempoRed.png', dpi=300)
    plt.close()

    # ==========================================
    # GRÁFICA 5.3: Respuestas Instantáneas
    # ==========================================
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df_agrupado, x='Escenario', y='Respuesta_SV_ms', palette='Oranges_d')
    plt.title('5.3. Tiempo de Respuesta del Servidor (Hardware/Kernel)', fontsize=14, fontweight='bold')
    plt.ylabel('Tiempo (ms)')
    plt.xlabel('Escenario de Prueba')
    plt.ylim(0, 0.6)
    
    for index, row in df_agrupado.iterrows():
        plt.text(index, row.Respuesta_SV_ms + 0.01, f'{row.Respuesta_SV_ms:.2f} ms', color='black', ha="center")
        
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('Grafica_5_3_RespuestaSV.png', dpi=300)
    plt.close()

    # ==========================================
    # GRÁFICA EXTRA: Descomposición del RTT Físico
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    escenarios = df_agrupado['Escenario']
    c_s = df_agrupado['Tiempo_C_S_ms']
    sv = df_agrupado['Respuesta_SV_ms']
    s_c = df_agrupado['Tiempo_S_C_ms']
    
    ax.bar(escenarios, c_s, label='Viaje Cliente -> Servidor (C_S)', color='#2ca02c') 
    ax.bar(escenarios, sv, bottom=c_s, label='Procesamiento Servidor (R_SV)', color='#ff7f0e') 
    ax.bar(escenarios, s_c, bottom=c_s + sv, label='Viaje Servidor -> Cliente (S_C)', color='#1f77b4') 
    
    ax.set_title('Descomposición del RTT Físico (ACKs Puros)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Tiempo (milisegundos)')
    ax.set_xlabel('Escenario de Prueba')
    
    # Escala detallada
    ax.set_ylim(0, 1.2)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.05))
    ax.grid(True, which='major', axis='y', linestyle='-', linewidth=0.8)
    ax.grid(True, which='minor', axis='y', linestyle=':', linewidth=0.5, alpha=0.7)
    
    ax.legend(loc='upper right')
    
    for i, (v1, v2, v3) in enumerate(zip(c_s, sv, s_c)):
        total = v1 + v2 + v3
        ax.text(i, total + 0.02, f'{total:.2f} ms', ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('Grafica_Descomposicion_RTT_Detallada.png', dpi=300)
    plt.close()

    # ==========================================
    # GRÁFICA 5.4: Análisis de Piggybacking
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    acks_puros = df_agrupado['Porcentaje_Instantaneo_num']
    piggybacking = df_agrupado['Piggybacked_num']
    
    ax.bar(escenarios, acks_puros, label='Paquetes ACK Puros (Control)', color='steelblue')
    ax.bar(escenarios, piggybacking, bottom=acks_puros, label='Paquetes ACK con Datos (Piggybacking)', color='lightcoral')
    
    ax.set_title('5.4. Proporción de Piggybacking vs ACKs Puros', fontsize=14, fontweight='bold')
    ax.set_ylabel('Proporción del Tráfico (%)')
    ax.set_xlabel('Escenario de Prueba')
    ax.set_ylim(0, 115) 
    ax.legend(loc='upper center', ncol=2)
    
    for i, (puro, piggy) in enumerate(zip(acks_puros, piggybacking)):
        if puro > 5:
            ax.text(i, puro/2, f'{puro:.1f}%', ha='center', va='center', color='white', fontweight='bold')
        if piggy > 5:
            ax.text(i, puro + piggy/2, f'{piggy:.1f}%', ha='center', va='center', color='white', fontweight='bold')
            
    plt.tight_layout()
    plt.savefig('Grafica_5_4_Piggybacking.png', dpi=300)
    plt.close()

    print("\n[OK] Proceso finalizado. Se han guardado 5 imágenes (.png) en la carpeta actual.")