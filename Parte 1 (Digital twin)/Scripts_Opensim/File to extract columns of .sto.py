import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
# -----------------------------
# FUNCION PARA LEER ARCHIVOS de activaciones de .sto DE OPENSIM y crear csv
# -----------------------------
def read_sto(filepath):
    """
    Lee un archivo .sto de OpenSim y devuelve:
    - lista de nombres de columnas
    - diccionario {col: numpy array}
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Encontrar 'endheader'
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("endheader"):
            start_idx = i + 1
            break

    if start_idx is None:
        raise ValueError("No se encontró 'endheader' en el archivo .sto")

    # Nombres de columnas
    header_line = lines[start_idx].strip()
    col_names = header_line.split()

    # Inicializar contenedor
    data = {col: [] for col in col_names}

    # Leer datos
    for line in lines[start_idx + 1:]:
        parts = line.strip().split()
        if len(parts) != len(col_names):
            continue
        for col, value in zip(col_names, parts):
            data[col].append(float(value))

    # Convertir listas a arrays
    for col in col_names:
        data[col] = np.array(data[col])

    return col_names, data


# -----------------------------
# LEER TU ARCHIVO .sto
# -----------------------------
sto_path = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/PRUEBA RESULTS/MoBL_ARMS_Upper_Limb_Model_OpenSim_StaticOptimization_activation_SUBJECT14_cond_ASS_PRE_FLEX.sto"

cols, d = read_sto(sto_path)
# -----------------------------

# -----------------------------
# EXTRAER COLUMNAS DE INTERÉS
# -----------------------------
time = d["time"]
ECRL = d["ECRL"]
ECRB = d["ECRB"]
FCR  = d["FCR"]
#defino el filtro butterworth
dt = np.median(np.diff(time))
fs_model = 1.0 / dt
print(f"Fs OpenSim ≈ {fs_model:.2f} Hz")

# -----------------------------


# -----------------------------
# GUARDAR NUEVO ARCHIVO CSV
# -----------------------------
output_path =  "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/PRUEBA RESULTS/Activations_ECR_FCR_SUBJECT14_cond_ASS_PRE_FLEX.csv"

out = np.column_stack((time, ECRL, ECRB, FCR))

np.savetxt(
    output_path,
    out,
    delimiter=",",
    header="time,ECRL,ECRB,FCR",
    comments="",
    fmt="%.7f"
)

print("Archivo creado correctamente en:")
print(output_path)

# 3. Graficar para comprobar que se importó bien
plt.figure()
plt.plot(time, ECRL, label="ECRL_trem", color='blue')
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud EMG")
plt.title("Activations ECRL (sincronizado y recortado)")
plt.grid(True)
plt.legend()
plt.show()

# --- Plot FCR ---
plt.figure()
plt.plot(time, FCR, label="FCR_trem", color='green')
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud EMG")
plt.title("Activations FCR (sincronizado y recortado)")
plt.grid(True)
plt.legend()
plt.show()

# 3. Graficar para comprobar que se importó bien
plt.figure()
plt.plot(time, ECRB, label="ECRB_trem", color='blue')
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud EMG")
plt.title("Activations ECRB (sincronizado y recortado)")
plt.grid(True)
plt.legend()
plt.show()
