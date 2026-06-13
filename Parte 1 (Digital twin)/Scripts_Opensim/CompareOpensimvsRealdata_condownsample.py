import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import resample
from scipy.signal import resample, correlate
import matplotlib as mpl

#Este codigo sirve para comparar activaciones open sim vs emg pero ambas teniendo la misma
# resolucion temporal (misma fs) y ademas incluyendo correlacion y todo.
# ==========================================
# 1. CONFIGURACIÓN Y RUTAS
# ==========================================

LAG_MANUAL = 0  # Sincronización del trigger
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10

path_opensim = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/PRUEBA RESULTS/Activations_ECR_FCR_SUBJECT14_cond_ASS_PRE_FLEX.csv"
path_emg = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/EMG_matlab_python/ECR_FCR_SUBJECT14_cond_PRE_FLEX_envelope.csv"

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

fs_target = 60  # Hz
fs_original=2000 #Hz por que el EMG orginal es a 2000 Hz
# Número de muestras nuevo
num_samples = int(len(fcr_emg_vis) * fs_target / fs_original)

# Resample
fcr_emg_vis_ds = resample(fcr_emg_vis, num_samples)
ecr_emg_vis_ds = resample(ecr_emg_vis, num_samples)

# Nuevo vector de tiempo
t_emg_ds = np.linspace(t_emg[0], t_emg[-1], num_samples)
print("Carga de datos completada con éxito.")

print(len(fcr_open), len(fcr_emg_vis_ds))
print(len(ecr_open), len(ecr_emg_vis_ds))

# Igualar longitudes
min_len = min(len(fcr_open), len(fcr_emg_vis_ds), len(ecr_open), len(ecr_emg_vis_ds))

fcr_open = fcr_open[:min_len]
fcr_emg_vis_ds = fcr_emg_vis_ds[:min_len]
ecr_open = ecr_open[:min_len]
ecr_emg_vis_ds = ecr_emg_vis_ds[:min_len]
t_open = t_open[:min_len]
t_emg_ds = t_emg_ds[:min_len]

# Métricas
mae_fcr = np.mean(np.abs(fcr_open - fcr_emg_vis_ds))
mae_ecr = np.mean(np.abs(ecr_open - ecr_emg_vis_ds))

corr_fcr = np.corrcoef(fcr_open, fcr_emg_vis_ds)[0, 1]
corr_ecr = np.corrcoef(ecr_open, ecr_emg_vis_ds)[0, 1]

xcorr_fcr = correlate(fcr_open - np.mean(fcr_open),
                      fcr_emg_vis_ds - np.mean(fcr_emg_vis_ds),
                      mode='full')

xcorr_ecr = correlate(ecr_open - np.mean(ecr_open),
                      ecr_emg_vis_ds - np.mean(ecr_emg_vis_ds),
                      mode='full')

lags = np.arange(-min_len + 1, min_len)

lag_fcr = lags[np.argmax(xcorr_fcr)]
lag_ecr = lags[np.argmax(xcorr_ecr)]

lag_fcr_sec = lag_fcr / fs_target
lag_ecr_sec = lag_ecr / fs_target

print("----- FCR -----")
print("MAE:", mae_fcr)
print("Correlation:", corr_fcr)
print("Max cross-correlation:", np.max(xcorr_fcr))
print("Lag máximo (samples):", lag_fcr)
print("Lag máximo (seconds):", lag_fcr_sec)

print("\n----- ECR -----")
print("MAE:", mae_ecr)
print("Correlation:", corr_ecr)
print("Max cross-correlation:", np.max(xcorr_ecr))
print("Lag máximo (samples):", lag_ecr)
print("Lag máximo (seconds):", lag_ecr_sec)
# ==========================================
# 3. GRÁFICA DE SOLAPE VISUAL
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)



# --- Músculo FCR ---
ax1.plot(t_open, fcr_open, label='OpenSim signal', color='blue', linewidth=2)
# Aplicamos el LAG al tiempo del EMG para alinearlo con OpenSim
ax1.plot(t_emg_ds - LAG_MANUAL, fcr_emg_vis_ds, label='EMG real signal', color='orange', alpha=0.4)
ax1.set_title("FCR: OpenSim vs EMG")
ax1.set_ylabel("Activation (0-1)")
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.2)

# --- Músculo ECR ---
ax2.plot(t_open, ecr_open, label='OpenSim signal', color='green', linewidth=2)
ax2.plot(t_emg_ds - LAG_MANUAL, ecr_emg_vis_ds, label='EMG real signal', color='red', alpha=0.4)
ax2.set_title("ECR: OpenSim vs EMG")
ax2.set_ylabel("Activation (0-1)")
ax2.set_xlabel("Time [s]")
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.2)

# Ajuste del eje X al rango de tus datos
plt.xlim([t_open[0], t_open[-1]])
plt.tight_layout()
plt.show()
