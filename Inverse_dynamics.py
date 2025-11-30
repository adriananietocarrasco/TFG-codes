#este code es para crear los mot y poder visualizar los en OpenSim
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx
from scipy.signal import butter, filtfilt

#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-POST-FLEX_run_01.mvnx"

#defino un band pass
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
        joint_angle = mvnx_file.get_joint_angle(
            idx,
            frame=mvn.FRAMES_ALL,
            angle=mvn.ANGLE_FLEXION_EXTENSION
        )
        print(joint_name)

        vec = np.asarray(joint_angle, dtype=float)
        print("vector shape:", vec.shape)
        print("primeros valores:", vec[:10])

        # ---- CREATE TIME COLUMN AT 6 Hz ----
        fs = float(frame_rate)  
        vec_tremor = bandpass_tremor(vec, fs)                    # sampling frequency (Hz), viene en el archivo
        N = len(vec)                      # number of samples
        time = np.arange(N) / fs          # time array (0, 1/6, 2/6, ...)
               # ---- FILTRAR: quedarnos solo con el TEMBLOR (4–12 Hz) ----
        fs = float(frame_rate)           # Hz (60)
        vec_tremor = bandpass_tremor(vec, fs)

        # ---- TIME COLUMN a fs (60 Hz) ----
        N = len(vec_tremor)
        time = np.arange(N) / fs        # 0, 1/fs, 2/fs, ...


                # ---- PLOT: crudo vs tremor ----
        plt.figure()
        plt.plot(time, vec_tremor, label='tremor (4–12 Hz)')
        plt.xlabel('time [s]')
        plt.ylabel('Amplitude [deg]')
        plt.title(f'({joint_name})')
        plt.legend()
        plt.show()
        # ---- BUILD 2-COLUMN MATRIX ----
        data_out = np.column_stack((time, vec_tremor))

        # ---- SAVE FILE ----
        output_dir = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/cvs_session1"
        os.makedirs(output_dir, exist_ok=True)

        out_csv = os.path.join(
            output_dir,
            f'joint_{idx}_{mvn.JOINTS[idx]}_flexion_ASS-POST-FLEX_run_01.mot'
        )

        # HEADER — no commas
        header = "time wrist_hand_r3_pos"

        # SAVE — space-separated, no commas
        np.savetxt(out_csv, data_out, fmt="%.6f", delimiter=' ', header=header, comments='')

        print("Guardado:", out_csv)

                # ---- SAVE AS .mot WITH OPENSIM-STYLE HEADER ----
        out_mot = os.path.join(
            output_dir,
            f'joint_{idx}_{mvn.JOINTS[idx]}_flexion_ASS-POST-FLEX_run_01_opensim.mot'
        )

        n_rows = len(time)
        header_lines = [
            "Coordinates",
            "version=1",
            f"nRows={n_rows}",
            "nColumns=2",
            "inDegrees=yes",
            "",
            "# Wrist tremor (filtered 4–12 Hz)",
            "endheader",
            "time\/jointset/wrist/wrist_flex/value"
        ]

        # convert header to single string
        header_str = "\n".join(header_lines)

        # np.savetxt solo permite un "header" string, así que:
        with open(out_mot, "w") as f:
            f.write(header_str + "\n")
            np.savetxt(f, data_out, fmt="%.6f", delimiter='\t')

        print("Guardado (OpenSim-style):", out_mot)
    
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

