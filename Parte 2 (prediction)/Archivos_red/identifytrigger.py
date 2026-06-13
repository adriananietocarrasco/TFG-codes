import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx
from scipy.signal import butter, filtfilt
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.io as sio
from scipy.interpolate import interp1d


mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10
#Este file lo que hace es obtener con 4 DOF
# , mas el tiempo los joints.mot para despues meterlos a open sim
#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = r"C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/20260305/XSENS/20260305_ADRIANA_test1.mvnx"
mat = sio.loadmat( r"C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/20260305/EMG_matlab/20260305_subject_01_cond_ASS-PRE-EXT-LEFT_run01_ecr_fcr_final.mat")  # cambia el nombre si hace falta

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


   
    # 2. Extraer las variables guardadas
    ECR = mat["ECR_final"].flatten()
    FCR = mat["FCR_final"].flatten()
    t   = mat["t_sync"].flatten()

    print("lengths:" , len(ECR), len(FCR), len(t))

    fig2, axs2 = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    plt.figure(figsize=(10, 6))
    plt.plot(time, flex_tremor, label="Flex Tremor", color="purple")
    plt.title("Angles vs time")
    plt.xlabel("time")
    plt.ylabel("angle (deg)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
  

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

    plt.tight_layout()
    

    #Recorte señales EMG:
    trigger= 8150
    ECR_recortado= ECR[trigger:]
    FCR_recortado= FCR[trigger:]
    print("lengths recortados:" , len(ECR_recortado), len(FCR_recortado))
    t_recortado= t[:168475] #168475 es el numero de muestras que quedan despues del trigger, lo calculo con el tiempo del wrist que es 88.3125s a 60Hz (88.3125*60=5298.75 muestras) y le sumo el trigger (8150+5298=13448) y me da el numero de muestras totales que tengo que recortar para quedarme solo con las muestras del wrist



    fig, axes = plt.subplots(2, 1, figsize=(11, 6), constrained_layout=True)

    axes[0].plot(t_recortado, ECR_recortado, color="blue", linewidth=1.5)
    axes[0].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("ECR")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(t_recortado, FCR_recortado, color="green", linewidth=1.5)
    axes[1].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("FCR")
    axes[1].legend()
    axes[1].grid(True)
#esta es la longitud real de la señal EMG; y se hace downsample a 60 Hz pero con su tiempo real. 
    t_start  = 0 
    t_end  =  84.2375 
    time_emg = np.arange(t_start, t_end, 1/60)  # vector a 60 Hz
    # Interpolar a los tiempos del wrist
    ECR_downsampled = np.interp(time_emg, t_recortado, ECR_recortado)
    FCR_downsampled = np.interp(time_emg, t_recortado, FCR_recortado)

    print("length ECR downsampled:", len(ECR_downsampled))
    print("length FCR downsampled:", len(FCR_downsampled))

    fig, axes = plt.subplots(2, 1, figsize=(11, 6), constrained_layout=True)

    axes[0].plot(time_emg, ECR_downsampled, color="blue", linewidth=1.5)
    axes[0].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("ECR")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(time_emg, FCR_downsampled, color="green", linewidth=1.5)
    axes[1].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("FCR")
    axes[1].legend()
    axes[1].grid(True)

    ECR_final= ECR_downsampled[:4295]
    FCR_final= FCR_downsampled[:4295]

    
    fig, axes = plt.subplots(3, 1, figsize=(11, 6), constrained_layout=True)

    axes[0].plot(time, flex_tremor, color="blue", linewidth=1.5)
    axes[0].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("angulos")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(time, ECR_final, color="green", linewidth=1.5)
    axes[1].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("ECR")
    axes[1].legend()
    axes[1].grid(True)
    
    axes[2].plot(time, FCR_final, color="blue", linewidth=1.5)
    axes[2].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("FCR")
    axes[2].legend()
    axes[2].grid(True)



    plt.show() 





   







if __name__ == '__main__':

    # Program entry point
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--mvnx_file', 
            required=False, 
            type=str, 
            default=("C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/20260305/XSENS/20260305_ADRIANA_test1.mvnx"),
            help='The MVNX file to load (defaults to EXT run 01)'
        )
    args = parser.parse_args()

try:
    main(args.mvnx_file)
except Exception as e:
    print("Error: %s" % e)