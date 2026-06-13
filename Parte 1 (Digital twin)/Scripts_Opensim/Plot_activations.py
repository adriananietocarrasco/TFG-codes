import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 10


def read_sto(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("endheader"):
            start_idx = i + 1
            break

    header_line = lines[start_idx].strip()
    column_names = header_line.split()

    data = {col: [] for col in column_names}

    for line in lines[start_idx + 1:]:
        parts = line.strip().split()
        if len(parts) != len(column_names):
            continue
        for col, value in zip(column_names, parts):
            data[col].append(float(value))

    return column_names, data


# ============= AJUSTA ESTA RUTA =============
sto_path = "C:/Users/adria/OneDrive/Documentos/Python-IMU/SUBJECT 14/SESSION 4/PRUEBA RESULTS/MoBL_ARMS_Upper_Limb_Model_OpenSim_StaticOptimization_activation_SUBJECT14_cond_ASS_PRE_FLEX.sto"
# ============================================

column_names, data = read_sto(sto_path)

time = data["time"]   # empezará en 4s porque así está en tu archivo
muscles = [c for c in column_names if c != "time"]

for m in muscles:
    plt.figure()
    plt.plot(time, data[m])
    plt.xlabel("Time [s]")
    plt.ylabel(f"{m} activation of OpenSim")
    plt.grid(True)
    plt.show()
    plt.close()
    