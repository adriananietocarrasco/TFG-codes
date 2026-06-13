#este file viene del file identify trigger (esta es la nueva versión)
#al usarlo:
# hay que cambiar la ruta de los archivos
# cambiar idx (9 para derecha y 13 para izquierda) 
# cambiar el nombre del archivo csv que se guarda al final. 

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx
from scipy.signal import butter, filtfilt
import matplotlib as mpl
import scipy.io as sio
from scipy.interpolate import interp1d


#ESTE ARCHIVO SIRVE PARA PLOTEAR LAS 3 GRÁFICAS A LA VEZ Y ELEGIR EL TRIGGER.

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10
#Este file lo que hace es obtener con 4 DOF
# , mas el tiempo los joints.mot para despues meterlos a open sim
#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = r"C:/Users/adria/Downloads/Python-IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-PRE-FLEX_run_01.mvnx"
mat = sio.loadmat( r"C:/Users/adria/Downloads/Python-IMU/SUBJECT 1/SESSION 1/EMG_matlab/20240115_subject_01_cond_ASS-PRE-FLEX-LEFT_run_01_fcr_ecr_final.mat")  # cambia el nombre si hace falta

#defino un band pass y un butterworth filter
# Filtro paso banda

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    #  angles_fil_values = signal.filtfilt(b, a, angles.values, padtype = 'odd', padlen=3*(max(len(b),len(a))-1), axis=0)
    return filtfilt(b, a, data)

# Convert mvnx file to python data
def main(file_name):
    # Check for file existence
    if not os.path.isfile(file_name):
        raise Exception("File %s could not be found" % file_name)

    tokens = file_name.lower().split('.')
    extension = tokens[-1]

    # Check for file extension
    if not extension == 'mvnx':
        raise Exception("File must be an .mvnx file")

    # Load data
    mvnx_file = load_mvnx(file_name)
    frame_rate = mvnx_file.frame_rate  # <<--- frecuencia real (e.g. 60 Hz)
    print("Frame rate:", frame_rate, "Hz")
    # Read some basic data from the file
    comments = mvnx_file.comments
    frame_rate = mvnx_file.frame_rate
    configuration = mvnx_file.configuration
    original_file_name = mvnx_file.original_file_name
    recording_date = mvnx_file.recording_date
    actor_name = mvnx_file.actor_name
    frame_count = mvnx_file.frame_count
    version = mvnx_file.version
    segment_count = mvnx_file.segment_count
    joint_count = mvnx_file.joint_count
#inverse_dynamics.py
    idx=13 #for wrist 9 for rigth and 13 for left
    joint_name = mvn.JOINTS[idx]
    joint_flex = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_FLEXION_EXTENSION
        )
    vec_flex = np.asarray(joint_flex, dtype=float)
    print("vector shape:", vec_flex.shape)
    print("primeros valores:", vec_flex[:10])





    # ---- CREATE TIME COLUMN AT  Hz ----
    fs = float(frame_rate)                   # sampling frequency (Hz), viene en el archivo
    N = len(vec_flex)                      # number of samples
    time = np.arange(N) / fs          # time array (0, 1/6, 2/6, ...)
            # ---- FILTRAR: quedarnos solo con el TEMBLOR (4–12 Hz) ----
    fs = float(frame_rate) # Hz (60)
    #con band pass entre 4-10 como Hajar
    flex_tremor = butter_bandpass_filter(vec_flex, 4.0, 10.0, fs)#joint_flex for wrist

        # ---- TIME COLUMN a fs (60 Hz) ----
  


                # ---- PLOT: crudo vs tremor ----
        # ---- RECORTAR SOLO LOS PRIMEROS 4 s ----
    Tmin = 0 # segundos
    idx_min = int(Tmin * fs)  # número de muestras a eliminar

    time = time[idx_min:]



    flex_tremor = flex_tremor[idx_min:]
    wrist_hand_r3_pos= flex_tremor

    idx_start = int(0 * fs)
    idx_end = int(30.6* fs)
    wrist_hand_r3_pos = wrist_hand_r3_pos[idx_start:idx_end]
    time_wrist = time[idx_start:idx_end]

    print(f"Rango de time_wrist: {time_wrist[0]:.4f} a {time_wrist[-1]:.4f} segundos")
    print(f"Longitud time_wrist: {len(time_wrist)}")
        # ---- BUILD 2-COLUMN MATRIX ----
   
    # 2. Extraer las variables guardadas
    ECR = mat["ECR_final"].flatten()
    FCR = mat["FCR_final"].flatten()
    t   = mat["t_sync"].flatten()

    fig2, axs2 = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

# --- 0. flex_tremor vs time ---
    axs2[0].plot(time, flex_tremor, label='Flex Tremor', color='purple')
    axs2[0].set_xlabel('Time [s]')
    axs2[0].set_ylabel('Angle (deg)')
    axs2[0].set_title('Flex Tremor - Full Signal')
    axs2[0].legend()
    axs2[0].grid(True)

    # --- 1. ECR vs t ---
    axs2[1].plot(t, ECR, label='ECR Original', color='blue')
    axs2[1].set_xlabel('Time [s]')
    axs2[1].set_ylabel('EMG Amplitude')
    axs2[1].set_title('EMG ECR LEFT')
    axs2[1].legend()
    axs2[1].grid(True)

    # --- 2. FCR vs t ---
    axs2[2].plot(t, FCR, label='FCR Original', color='green')
    axs2[2].set_xlabel('Time [s]')
    axs2[2].set_ylabel('EMG Amplitude')
    axs2[2].set_title('EMG FCR LEFT')
    axs2[2].legend()
    axs2[2].grid(True)

    # Crear  de interpolación
    ECR_interp = interp1d(t, ECR, kind="linear", bounds_error=False, fill_value="extrapolate")
    FCR_interp = interp1d(t, FCR, kind="linear", bounds_error=False, fill_value="extrapolate")
    
    # Tu rango objetivo (ajustar al rango de time_wrist)

    t_start  = 3.0435
    t_end  =  33.6435
    time_emg = np.arange(t_start, t_end, 1/60)  # vector a 60 Hz
    # Interpolar a los tiempos del wrist
    ECR_act = ECR_interp(time_emg)
    FCR_act = FCR_interp(time_emg)
    # t ya está en segundos, no necesita conversió
    
    # Máscara lógica para quedarte solo con ese rango
    mask_emg = (time_emg >= t_start) & (time_emg <= t_end)

    
    print(f"Rango EMG: {time_emg[0]:.4f} a {time_emg[-1]:.4f} segundos")
    print(f"Longitud EMG: {len(time_emg)}")
    
    # Verificar que los rangos se solapen
    if len(time_emg) == 0:
        raise Exception("No hay datos EMG en el rango especificado")
    if len(time_wrist) == 0:
        raise Exception("No hay datos de wrist en el rango especificado")


    print("Tiempo recortado:", time_emg[0], "hasta", time_emg[-1])
    print("Longitud:", len(time_emg))
    print("Longitud wrist_hand_r3_pos:", len(wrist_hand_r3_pos))
    print("Longitud time_wrist:", len(time_wrist))

    N_samples = len(ECR_act)  # 3384 muestras
    time_common = np.arange(N_samples) / 60
    
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=False)
    N_samples = len(ECR_act)  # 3384 muestras
    time_common = np.arange(N_samples) / 60
    # --- 1. Flexión–Extensión filtrada ---
    axs[0].plot(time_common, wrist_hand_r3_pos, label='Filtered (4–10 Hz)')
    axs[0].set_xlabel('Time [s]')
    axs[0].set_ylabel('Angle (deg)')
    axs[0].set_title('Left Wrist Flexion–Extension')
    axs[0].legend()
    axs[0].grid(True)

    # --- 2. EMG ECR ---
    axs[1].plot(time_common, ECR_act, label='ECR', color='blue')
    axs[1].set_xlabel('Time [s]')
    axs[1].set_ylabel('EMG Amplitude')
    axs[1].set_title('EMG ECR LEFT')
    axs[1].legend()
    axs[1].grid(True)

    # --- 3. EMG FCR ---
    axs[2].plot(time_common, FCR_act, label='FCR', color='green')
    axs[2].set_xlabel('Time [s]')
    axs[2].set_ylabel('EMG Amplitude')
    axs[2].set_title('EMG FCR LEFT')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


    # 4. Guardar en un archivo con 4 columnas: tiempo, ECR, FCR, wrist
    #    Lo guardamos como .csv (lo puedes abrir con Excel, etc.)
    
    # Todas las señales ya tienen la misma longitud (time_wrist)
# quitar los primeros 8 segundos (8 * 60 = 480 muestras)
   # samples_to_remove = int(8 * 60)

    #datos = np.column_stack((
      #  ECR_act[samples_to_remove:], 
       # FCR_act[samples_to_remove:], 
       # wrist_hand_r3_pos[samples_to_remove:]
   # ))
    datos = np.column_stack((
        ECR_act, 
        FCR_act, 
        wrist_hand_r3_pos
    ))
    
    np.savetxt(
        "C:/Users/adria/Downloads/Python-IMU/SUBJECT 1/EMG_matlab/20240115_subject_01_cond_ASS-PRE-FLEX-LEFT_run_01_ecr_fcr_final.csv",  # CAMBIA LA RUTA/NOMBRE
        datos,
        delimiter=",",
        header="ECR_act,FCR_act,wrist_hand_r3_pos",
        comments="",       # para que no ponga '#' delante del header
        fmt="%.6f"         # formato de números (6 decimales)
    )

    print("Archivo guardado correctamente :)")
    print(f"Número de muestras guardadas: {len(time_wrist)}")

if __name__ == '__main__':

    # Program entry point
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--mvnx_file', 
            required=False, 
            type=str, 
            default=("C:/Users/adria/Downloads/Python-IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-PRE-FLEX_run_01.mvnx"),
            help='The MVNX file to load (defaults to EXT run 01)'
        )
    args = parser.parse_args()

try:
    main(args.mvnx_file)
except Exception as e:
    print("Error: %s" % e)