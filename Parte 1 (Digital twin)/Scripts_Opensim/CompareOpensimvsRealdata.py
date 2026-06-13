import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. CONFIGURACIÓN Y RUTAS
# ==========================================
LAG_MANUAL = 0  # Sincronización del trigger

path_opensim = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 1/SESSION 1/PRUEBA RESULTS/Activations_ECR_FCR_SUBJECT1_cond_ASS_POST_FLEX.csv"
path_emg = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 1/SESSION 1/EMG_matlab_python/ECR_FCR_SUBJECT1_cond_POST_FLEX_envelope.csv"
# ==========================================
# ==========================================
# 2. CARGA Y PROCESAMIENTO (CORREGIDO)
# ==========================================
df_open = pd.read_csv(path_opensim)
df_emg = pd.read_csv(path_emg)

# Limpiamos posibles espacios en blanco en los títulos por seguridad
df_open.columns = df_open.columns.str.strip()
df_emg.columns = df_emg.columns.str.strip()

# OpenSim: Usamos los nombres estándar de OpenSim
t_open = df_open['time'].values
fcr_open = df_open['FCR'].values
# Promediamos los extensores (Longus y Brevis) para comparar con el único sensor ECR real
ecr_open = (df_open['ECRL'].values + df_open['ECRB'].values) / 2 

# EMG: Usamos los nombres EXACTOS que me has pasado del CSV
t_emg = df_emg['time'].values
fcr_emg_vis = df_emg['FCR_normalizado'].values 
ecr_emg_vis = df_emg['ECR_normalizado'].values

print("Carga de datos completada con éxito.")

# ==========================================
# 3. GRÁFICA DE SOLAPE VISUAL
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# --- Músculo FCR ---
ax1.plot(t_open, fcr_open, label='OpenSim (Original)', color='blue', linewidth=2)
# Aplicamos el LAG al tiempo del EMG para alinearlo con OpenSim
ax1.plot(t_emg - LAG_MANUAL, fcr_emg_vis, label='EMG (Rectificado + Normalizado)', color='orange', alpha=0.4)
ax1.set_title("FCR: OpenSim vs EMG")
ax1.set_ylabel("Activación (0-1)")
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.2)

# --- Músculo ECR ---
ax2.plot(t_open, ecr_open, label='OpenSim (Original)', color='green', linewidth=2)
ax2.plot(t_emg - LAG_MANUAL, ecr_emg_vis, label='EMG (Rectificado + Normalizado)', color='red', alpha=0.4)
ax2.set_title("ECR: OpenSim vs EMG")
ax2.set_ylabel("Activación (0-1)")
ax2.set_xlabel("Tiempo (segundos)")
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.2)

# Ajuste del eje X al rango de tus datos
plt.xlim([t_open[0], t_open[-1]])
plt.tight_layout()
plt.show()
