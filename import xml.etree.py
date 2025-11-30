import xml.etree.ElementTree as ET
import numpy as np

def mvnx_to_mot(mvnx_path, mot_path):
    # 1. Leer XML de Xsens
    tree = ET.parse(mvnx_path)
    root = tree.getroot()
    ns = {"m": root.tag.split('}')[0].strip('{')}

    # 2. Sacar info del sujeto
    subj = root.find("m:subject", ns)
    fps = float(subj.attrib["frameRate"])   # p.ej. 60 Hz
    frames = list(subj.find("m:frames", ns))

    # 3. Buscar primer frame que tenga jointAngle
    start_idx = 0
    for i, fr in enumerate(frames):
        if fr.find("m:jointAngle", ns) is not None:
            start_idx = i
            break

    # 4. Orden de las articulaciones
    joints = subj.find("m:joints", ns)
    joint_labels = [j.attrib["label"] for j in joints]

    elbow_idx = joint_labels.index("jRightElbow")
    wrist_idx = joint_labels.index("jRightWrist")

    def get_joint_angles_for_frame(fr):
        ja = fr.find("m:jointAngle", ns)
        if ja is None or ja.text is None:
            return None
        return list(map(float, ja.text.strip().split()))

    all_vals = []
    for fr in frames[start_idx:]:
        vals = get_joint_angles_for_frame(fr)
        if vals is not None:
            all_vals.append(vals)

    A = np.array(all_vals)  # shape: [N_frames, 66]

    def block(A, joint_index):
        i = joint_index * 3
        return A[:, i:i+3]

    elbow = block(A, elbow_idx)  # columnas 0,1,2 (del codo)
    wrist = block(A, wrist_idx)  # columnas 0,1,2 (de la muñeca)

    # 5. Mapear ejes de Xsens → DOFs de OpenSim
    elbow_flexion = elbow[:, 1]   # gran rango 60–140°
    pro_sup       = elbow[:, 2]   # 20–80°
    flexion       = wrist[:, 2]   # -60 – -25° (flex/ext)
    deviation     = wrist[:, 1]   # ~±20° (radial/ulnar)

    # 6. Vector de tiempo (empieza en 0; si quieres absoluto, suma start_idx/fps)
    time = np.arange(len(elbow_flexion)) / fps

    # 7. Escribir archivo .mot
    nRows = len(time)
    nColumns = 5  # time + 4 DOFs

    with open(mot_path, "w") as f:
        f.write("Coordinates\n")
        f.write("version=1\n")
        f.write(f"nRows={nRows}\n")
        f.write(f"nColumns={nColumns}\n")
        f.write("inDegrees=yes\n")
        f.write("endheader\n")
        f.write("time\telbow_flexion\tpro_sup\tflexion\tdeviation\n")
        for t, ef, ps, fl, dv in zip(time, elbow_flexion, pro_sup, flexion, deviation):
            f.write(f"{t:.5f}\t{ef:.6f}\t{ps:.6f}\t{fl:.6f}\t{dv:.6f}\n")

    print("Hecho.")
    print("FPS:", fps)
    print("Primer frame con jointAngle:", start_idx)
    print("Joint labels:", joint_labels)

# ---- USO ----
if __name__ == "__main__":
    mvnx_path = "20240227_subject_03_cond_ASS-POST-EXT_run_01.mvnx"  # tu archivo
    mot_path  = "subject03_ASS_POST_EXT_jointangles.mot"             # salida
    mvnx_to_mot(mvnx_path, mot_path)
