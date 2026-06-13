import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np

# 1. Cargar el archivo .mat
mat = sio.loadmat( "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/EMG_matlab_python/ECR_FCR_SUBJECT14_cond_PRE_FLEX_envelope.mat")  # cambia el nombre si hace falta

# 2. Extraer las variables guardadas
ECR = mat["ECR_final"].flatten()
FCR = mat["FCR_final"].flatten()
t   = mat["t_sync"].flatten()

import numpy as np

# Tu rango objetivo
t_start = 4.0
t_end  =   41.9655


# Máscara lógica para quedarte solo con ese rango
mask = (t >= t_start) & (t <= t_end)

# Recortes
t_recortada  = t[mask]
ECR_recortada = ECR[mask]
FCR_recortada = FCR[mask]

print("Tiempo recortado:", t_recortada[0], "hasta", t_recortada[-1])
print("Longitud:", len(t_recortada))

# 4. Guardar en un archivo con 3 columnas: tiempo, ECR, FCR
#    Lo guardamos como .csv (lo puedes abrir con Excel, etc.)
datos = np.column_stack((t_recortada, ECR_recortada, FCR_recortada))
np.savetxt(
    "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/EMG_matlab_python/ECR_FCR_SUBJECT14_cond_PRE_FLEX_envelope.csv",  # CAMBIA LA RUTA/NOMBRE
    datos,
    delimiter=",",
    header="time,ECR_normalizado,FCR_normalizado",
    comments="",       # para que no ponga '#' delante del header
    fmt="%.6f"         # formato de números (6 decimales)
)

print("Archivo guardado correctamente :)")

# 3. Graficar para comprobar que se importó bien
plt.figure()
plt.plot(t_recortada, ECR_recortada, label="ECR_normalizado", color='blue')
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud EMG")
plt.title("EMG ECR (sincronizado y recortado)")
plt.grid(True)
plt.legend()
plt.show()

# --- Plot FCR ---
plt.figure()
plt.plot(t_recortada, FCR_recortada, label="FCR_normalizado", color='green')
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud EMG")
plt.title("EMG FCR (sincronizado y recortado)")
plt.grid(True)
plt.legend()
plt.show()
