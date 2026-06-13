import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10
#Este file lo que hace es obtener con 4 DOF
# , mas el tiempo los joints.mot para despues meterlos a open sim
#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = "C:/Users/adria/Downloads/Python-IMU/Adriana-Neuroengineering_lab/20260525/test_01.mvnx"

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
    idx= 9 #for wrist rigth
    joint_name = mvn.JOINTS[idx]
    joint_flex = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_FLEXION_EXTENSION
        )
    vec_flex = np.asarray(joint_flex, dtype=float)
    print("vector shape:", vec_flex.shape)
    print("primeros valores:", vec_flex[:10])


    plt.figure(idx)
    plt.plot(joint_flex)
    plt.xlabel('Samples')
    plt.ylabel('Right wrist Flexion–Extension Angle (deg)')
    plt.legend(['z'])
    plt.draw()
    plt.show() 


#ME HE QUEDADO AQUI DIA 17 DE NOVIEMBRE 2023
    # ---- CREATE TIME COLUMN AT 6 Hz ----
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
    Tmin = 4.0  # segundos
    idx_min = int(Tmin * fs)  # número de muestras a eliminar

    time = time[idx_min:]
    flex_tremor = flex_tremor[idx_min:]


        # ---- BUILD 2-COLUMN MATRIX ----
    data_out = np.column_stack((time, flex_tremor))
    # ---- SAVE FILE ----"C:/Users/adria/Documents/Python-IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-POST-FLEX_run_01.mvnx"
    output_dir = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/cvs_session4"
    os.makedirs(output_dir, exist_ok=True)

            # ---- SAVE AS .mot WITH OPENSIM-STYLE HEADER ----
    out_mot = os.path.join(
        output_dir,
        f'joint_{idx}_{mvn.JOINTS[idx]}_cond_ASS-PRE-FLEX_run_01_filtroHAJAR_flex.mot'
    )

    n_rows = len(time)
    header_lines = [
        "Coordinates",
        "version=1",
        f"nRows={n_rows}",
        "nColumns=2",
        "inDegrees=yes",
        "",
        "# Wrist tremor (filtered 4-10 Hz)",
        "endheader",
        "time  flexion"

    ]


    # convert header to single string
    header_str = "\n".join(header_lines)

    # np.savetxt solo permite un "header" string, así que:
    with open(out_mot, "w") as f:
        f.write(header_str + "\n")
        np.savetxt(f, data_out, fmt="%.6f", delimiter='\t')
            
    plt.figure()
    plt.plot(time,flex_tremor, label='Filtered (4-10 Hz)')
    plt.xlabel('time [s]')
    plt.ylabel('Right wrist Flexion–Extension Angle (deg)')
    plt.legend()
  

    plt.savefig(f"C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/SESSION 4_plots/joint_{idx}_{mvn.JOINTS[idx]}_cond_ASS-PRE-FLEX_run_01_filtroHAJAR_flex.plot.png")
    plt.show()
if __name__ == '__main__':

# Program entry point
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mvnx_file', 
        required=False, 
        type=str, 
        default=("C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/XSens output/"
                "20250617_subject_14_cond_ASS-PRE-FLEX_run_01.mvnx"),
        help='The MVNX file to load (defaults to EXT run 01)'
    )
    args = parser.parse_args()

try:
    main(args.mvnx_file)
except Exception as e:
    print("Error: %s" % e)