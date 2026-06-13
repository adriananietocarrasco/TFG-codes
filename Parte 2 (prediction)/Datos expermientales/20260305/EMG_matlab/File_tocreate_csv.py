#Uso este file para crear un csv nuevo de los pacientes, que tengan de columnas wrist position, ECR y FCR y se pueda usar para entrenar la red.

import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# =========================
# RUTAS DE ENTRADA
# =========================
emg_file = Path(r"C:\Users\adria\OneDrive\Documentos\Python-IMU\SUBJECT 1\SESSION 1\EMG_matlab_python\ECR_FCR_SUBJECT1_cond_PRE_FLEX_envelope.csv")
mot_file = Path(r"C:\Users\adria\Downloads\Python-IMU\SUBJECT 1\SESSION 1\cvs_session1\joint_9_jRightWrist_cond_ASS-PRE-FLEX_run_01_filtroHAJAR_flex.mot")

# =========================
# RUTA DE SALIDA
# =========================
output_file = Path(r"C:\Users\adria\Downloads\Python-IMU\Adriana-Neuroengineering_lab\20260305\EMG_matlab\20260305_subject_01_cond_ASS-PRE-EXT-RIGHT_run05_ecr_fcr_final.csv")


# =========================
# 1. LEER CSV DE EMG
# =========================
df_emg = pd.read_csv(emg_file)

# Comprobar que existen las columnas necesarias
required_emg_cols = ["ECR_normalizado", "FCR_normalizado"]
for col in required_emg_cols:
    if col not in df_emg.columns:
        raise ValueError(f"No se encontró la columna '{col}' en el archivo EMG.")

# Renombrar columnas al formato final
df_emg_selected = df_emg[["ECR_normalizado", "FCR_normalizado"]].copy()
df_emg_selected.columns = ["ECR_act", "FCR_act"]


# =========================
# 2. LEER ARCHIVO .MOT
# =========================
# Un .mot suele tener cabecera de texto y luego una tabla.
# Buscamos la línea donde aparece el nombre de las columnas.
with open(mot_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

header_line_idx = None
for i, line in enumerate(lines):
    # Quitamos espacios laterales y dividimos por espacios/tabulaciones
    parts = line.strip().split()
    if "flexion" in parts:
        header_line_idx = i
        break

if header_line_idx is None:
    raise ValueError("No se encontró la fila de cabecera con la columna 'flexion' en el archivo .mot.")

# Leer la tabla desde la cabecera detectada
df_mot = pd.read_csv(
    mot_file,
    sep=r"\s+",
    engine="python",
    skiprows=header_line_idx
)

# Comprobar que existe la columna flexion
if "flexion" not in df_mot.columns:
    raise ValueError("No se encontró la columna 'flexion' en el archivo .mot después de cargarlo.")

# Seleccionar y renombrar
df_mot_selected = df_mot[["flexion"]].copy()
df_mot_selected.columns = ["wrist_hand_r3_pos"]


# =========================
# 3. IGUALAR LONGITUDES
# =========================
min_len = min(len(df_emg_selected), len(df_mot_selected))

df_final = pd.DataFrame({
    "ECR_act": df_emg_selected["ECR_act"].iloc[:min_len].reset_index(drop=True),
    "FCR_act": df_emg_selected["FCR_act"].iloc[:min_len].reset_index(drop=True),
    "wrist_hand_r3_pos": df_mot_selected["wrist_hand_r3_pos"].iloc[:min_len].reset_index(drop=True)
})


# =========================
# 4. GUARDAR CSV FINAL
# =========================
df_final.to_csv(output_file, index=False)

print("CSV creado correctamente en:")
print(output_file)
print(f"Número de filas guardadas: {len(df_final)}")
print(df_final.head())


t = np.arange(len(df_final))  # eje temporal (muestras)

plt.figure(figsize=(12, 8))

# ---- ECR ----
plt.subplot(3, 1, 1)
plt.plot(t, df_final["ECR_act"], color='green')
plt.title("ECR Activation")
plt.ylabel("ECR_act")
plt.grid()

# ---- FCR ----
plt.subplot(3, 1, 2)
plt.plot(t, df_final["FCR_act"], color='orange')
plt.title("FCR Activation")
plt.ylabel("FCR_act")
plt.grid()

# ---- Wrist angle ----
plt.subplot(3, 1, 3)
plt.plot(t, df_final["wrist_hand_r3_pos"], color='blue')
plt.title("Wrist Flexion (wrist_hand_r3_pos)")
plt.xlabel("Samples")
plt.ylabel("Angle")
plt.grid()

plt.tight_layout()
plt.show()