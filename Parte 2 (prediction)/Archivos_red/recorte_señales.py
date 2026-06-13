import os
import pandas as pd

# Este code es para recortas señales de un csv por si despues de la sincronización ha habido error
INPUT_FILE = "C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/Archivos_red/20260305_subject_01_cond_ASS-PRE-EXT-RIGHT_run03_ecr_fcr_final.csv"
OUTPUT_DIR = r"C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/Archivos_red/Recortes"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "20260305_subject_01_cond_ASS-PRE-EXT-RIGHT_run03_ecr_fcr_final_recortado.csv")

# Asegurar que la carpeta de destino existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Cargar datos originales
df = pd.read_csv(INPUT_FILE)

print(f"Archivo original cargado. Total de muestras disponibles: {len(df)}")

#estas siguientes líneas son para definir el inicio y final del archivo

ecr_recortado = df["ECR_act"].iloc[:].reset_index(drop=True)
fcr_recortado = df["FCR_act"].iloc[:].reset_index(drop=True)
wrist_recortado = df["wrist_hand_r3_pos"].iloc[:].reset_index(drop=True)

# Juntar los vectores recortados
df_final = pd.DataFrame(
    {
        "ECR_act": ecr_recortado,
        "FCR_act": fcr_recortado,
        "wrist_hand_r3_pos": wrist_recortado,
    }
)

# 5. Guardar el resultado en el nuevo CSV
# index=False evita que se guarde una columna extra con los números de fila nuevos
df_final.to_csv(OUTPUT_FILE, index=False)

print("\n¡Recorte por muestras completado con éxito!")
print(f"Archivo nuevo guardado en: {OUTPUT_FILE}")
print(f"Nueva longitud máxima de filas: {len(df_final)}")