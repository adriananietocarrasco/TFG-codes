import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import mvn #hay que importar este por que tiene datos de los segments y joints y angles
from load_mvnx import load_mvnx

#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/XSens output/20240115_subject_01_cond_ASS-POST-FLEX_run_01.mvnx"

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

#en este for se plotean 2 graficas para 9 y 13
    for idx in [9, 13]:
        joint_name = mvn.JOINTS[idx]
        joint_angle = mvnx_file.get_joint_angle(idx, frame=mvn.FRAMES_ALL, angle=mvn.ANGLE_FLEXION_EXTENSION)
        print (joint_name)  
        vec = np.asarray(joint_angle, dtype=float)   # este es el vector que quieres, y por ello he importado mumpy
        print("vector shape:", vec.shape)
        print("todos los valores:", vec[:10])

        output_dir = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 1/SESSION 1/cvs_session1"  # o ruta relativa "outputs"
        os.makedirs(output_dir, exist_ok=True)

        
        out_csv = os.path.join(output_dir, f'joint_{idx}_{mvn.JOINTS[idx]}_flexion_ASS-POST-FLEX_run_01.csv')
        if idx ==9:
            header= 'wrist_hand_r3_pos'
            np.savetxt(out_csv, vec, delimiter=',', header=header, comments='')
            print("Guardado:", out_csv)
        if idx ==13:
            header= 'wrist_hand_r3_pos'
            np.savetxt(out_csv, vec, delimiter=',', header=header, comments='')
            print("Guardado:", out_csv)


        plt.figure(idx)
        plt.plot(joint_angle)
        plt.xlabel('frames')
        plt.ylabel('Amplitude in degrees')
        plt.title('Amplitude in degrees ' + joint_name + ' joint')
        plt.legend(['z'])
        plt.draw()
        plt.show() 
    # Alternatively, use the generic method get_data() with the data set and field. E.g.:
    # segment_pos = mvnx_file.get_data('segment_data', 'pos', idx)
    #EN Este code, he añadido angle_pronation_supination para la muñeca izquierda , y asi comparar con la flexion extension
    
    # Read the data from the structure e.g. first segment. HAY QUE CAMBIARLO SEGUN EL INDICE QUE SE QIUIERS
    # Tengo que save cada vez que cambio el indice
    

    # Alternatively, use the generic method get_data() with the data set and field. E.g.:
    # segment_pos = mvnx_file.get_data('segment_data', 'pos', idx)
    plt.show() 



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
