import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# Configuración estética para el TFG
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10

# ==========================================
# 1. CONFIGURACIÓN Y RUTAS
# ==========================================
path_emg = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 1/SESSION 1/EMG_matlab_python/ECR_FCR_SUBJECT1_cond_PRE_FLEX_envelope.csv"

# Ruta y nombre exacto para guardar en tu OneDrive
dir_guardado = r"C:\Users\adria\OneDrive\TFG\PARTE 1-GRÁFICAS\PACIENTE 1\SESSION 1"
nombre_archivo = "20240115_subject_01_cond_ASS-PRE-FLEX_run_01.png"
path_salida_completo = os.path.join(dir_guardado, nombre_archivo)

# ==========================================
# 2. CARGA Y PROCESAMIENTO
# ==========================================
df_emg = pd.read_csv(path_emg)

# Limpiamos posibles espacios en blanco en los títulos por seguridad
df_emg.columns = df_emg.columns.str.strip()

# EMG: Usamos los nombres EXACTOS del CSV
t_emg = df_emg['time'].values
fcr_emg_vis = df_emg['FCR_normalizado'].values 
ecr_emg_vis = df_emg['ECR_normalizado'].values

print("Carga de datos completada con éxito.")

# ==========================================
# 3. DISEÑO DE SUBPLOTS (ECR y FCR)
# ==========================================
# sharex=True vincula los ejes X para que el zoom o paneo afecte a ambas señales a la vez
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# --- Subplot Superior: Músculo ECR ---
axes[0].plot(t_emg, ecr_emg_vis, color="purple", linewidth=1.2, label="Normalized ECR")
axes[0].set_title("ECR real muscle activations", fontweight='bold')
axes[0].set_ylabel("Muscle Activation (0-1)")
axes[0].legend(loc="upper right")
axes[0].grid(True, linestyle=":", alpha=0.6)

# --- Subplot Inferior: Músculo FCR ---
axes[1].plot(t_emg, fcr_emg_vis, color="chocolate", linewidth=1.2, label="Normalized FCR")
axes[1].set_title("FCR real muscle activations", fontweight='bold')
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Muscle Activation (0-1)")
axes[1].legend(loc="upper right")
axes[1].grid(True, linestyle=":", alpha=0.6)

# Ajuste automático de márgenes para evitar solapamiento de textos
plt.tight_layout()

# ==========================================
# 4. GUARDADO AUTOMÁTICO EN ONEDRIVE
# ==========================================
# Crea la estructura de carpetas si no existiera en el equipo actual
os.makedirs(dir_guardado, exist_ok=True)

# Guardado en alta resolución (dpi=300) y ajustando bordes
plt.savefig(path_salida_completo, dpi=300, bbox_inches='tight')
print(f"✅ Gráfica guardada correctamente en:\n👉 {path_salida_completo}")

# Mostrar por pantalla
plt.show()