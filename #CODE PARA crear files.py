#CODE PARA crear files.mot con todas las columnas necesarias
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx
from scipy.signal import butter, filtfilt

#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-POST-FLEX_run_01.mvnx"

#defino un band pass y un butterworth filter
def bandpass_centered(signal, fs, fc=9, bandwidth=7, order=3):

    half_bw = bandwidth / 2.0
    f_low  = fc - half_bw
    f_high = fc + half_bw
    nyq = 0.5 * fs
    low = f_low / nyq
    high = f_high / nyq
    if low <= 0:
        low = 1e-6
    if high >= 1:
        high = 0.999999
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)

def bandpass_tremor(signal, fs, f_low=4.0, f_high=12.0, order=4):
    """Band-pass filter to isolate tremor component (en Hz)."""
    nyq = 0.5 * fs
    low = f_low / nyq
    high = f_high / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)
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
    for idx in [9, 13]:
        joint_name = mvn.JOINTS[idx]
        joint_flex = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_FLEXION_EXTENSION
        )
        vec_flex = np.asarray(joint_flex, dtype=float)
        print("vector shape:", vec_flex.shape)
        print("primeros valores:", vec_flex[:10])

        joint_dev = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_ABDUCTION_ADDUCTION   # <-- si tu librería usa otro nombre, cámbialo aquí
        )
        vec_dev = np.asarray(joint_dev, dtype=float)

        joint_sup = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_PRONATION_SUPINATION   # <-- si tu librería usa otro nombre, cámbialo aquí
        )
        vec_sup = np.asarray(joint_sup, dtype=float)
        
        
    

#ME HE QUEDADO AQUI DIA 17 DE NOVIEMBRE 2023
        # ---- CREATE TIME COLUMN AT 6 Hz ----
        fs = float(frame_rate)                   # sampling frequency (Hz), viene en el archivo
        N = len(vec_flex)                      # number of samples
        time = np.arange(N) / fs          # time array (0, 1/6, 2/6, ...)
               # ---- FILTRAR: quedarnos solo con el TEMBLOR (4–12 Hz) ----
        fs = float(frame_rate) # Hz (60)
        #con band pass
        flex_tremor = bandpass_tremor(vec_flex, fs)#joint_flex
        dev_tremor  = bandpass_tremor(vec_dev,  fs)#joint_dev
        sup_tremor  = bandpass_tremor(vec_sup,  fs)#joint_sup
        #con butter
        flex_tremor1 = bandpass_centered(vec_flex, fs)#joint_flex
        dev_tremor1 = bandpass_centered(vec_dev,  fs)#joint_dev
        sup_tremor1 = bandpass_centered(vec_sup,  fs)#joint_sup
    
        # ---- TIME COLUMN a fs (60 Hz) ----
  


                # ---- PLOT: crudo vs tremor ----

        # ---- BUILD 2-COLUMN MATRIX ----
        data_out = np.column_stack((time, flex_tremor1, dev_tremor1, sup_tremor1))

        # ---- SAVE FILE ----
        output_dir = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/cvs_session1"
        os.makedirs(output_dir, exist_ok=True)

                # ---- SAVE AS .mot WITH OPENSIM-STYLE HEADER ----
        out_mot = os.path.join(
            output_dir,
            f'joint_{idx}_{mvn.JOINTS[idx]}_flexion_ASS-POST-FLEX_run_01_7Hzfiltro.mot'
        )

        n_rows = len(time)
        header_lines = [
            "Coordinates",
            "version=1",
            f"nRows={n_rows}",
            "nColumns=4",
            "inDegrees=yes",
            "",
            "# Wrist tremor (filtered 7 Hz)",
            "endheader",
            "time  flexion   deviation   pro_sup"

        ]

        # convert header to single string
        header_str = "\n".join(header_lines)

        # np.savetxt solo permite un "header" string, así que:
        with open(out_mot, "w") as f:
            f.write(header_str + "\n")
            np.savetxt(f, data_out, fmt="%.6f", delimiter='\t')

        print("Guardado (OpenSim-style):", out_mot)
        plt.figure()
        plt.plot(time,flex_tremor, label='tremor (7Hz)')
        plt.xlabel('time [s]')
        plt.ylabel('Amplitude [deg]')
        plt.title(f'({joint_name})')
        plt.legend()
        plt.show()


        #aqui de nuevo
        data_out1 = np.column_stack((time, flex_tremor1))
        out_mot = os.path.join(
        output_dir,
        f'joint_{idx}_{mvn.JOINTS[idx]}_flexion_ASS-POST-FLEX_run_01_flex.mot'
        )

        n_rows = len(time)
        header_lines = [
            "Coordinates",
            "version=1",
            f"nRows={n_rows}",
            "nColumns=2",
            "inDegrees=yes",
            "",
            "# Wrist tremor (filtered 7Hz)",
            "endheader",
            "time  flexion "

        ]

        header_str = "\n".join(header_lines)

        # SAVE — space-separated, no commas
        with open(out_mot, "w") as f:
            f.write(header_str + "\n")
            np.savetxt(f, data_out1, fmt="%.6f", delimiter='\t')


if __name__ == '__main__':

# Program entry point
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mvnx_file', 
        required=False, 
        type=str, 
        default=("/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/XSens output/"
                "20240115_subject_01_cond_ASS-POST-FLEX_run_01.mvnx"),
        help='The MVNX file to load (defaults to ASS-POST-FLEX run 01)'
    )
    args = parser.parse_args()

    try:
        main(args.mvnx_file)
    except Exception as e:
        print("Error: %s" % e)

