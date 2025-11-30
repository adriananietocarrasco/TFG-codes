"""
Example: How to read .sto file and extract columns into 2D vectors
"""
#ESTE FILE HA SIDO CREADO PARA LEER ARCHIVOS .STO DE OPENSIM Y EXTRAER LAS COLUMNAS EN VECTORES 2D. Y PLOTEAR LAS ACTIVATIONS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def read_sto_file(sto_path):
    """
    Reads an OpenSim .sto file and returns a pandas DataFrame.
    
    Args:
        sto_path: Path to the .sto file
        
    Returns:
        DataFrame with columns from the .sto file
    """
    # Find where the header ends (look for "endheader")
    with open(sto_path, 'r') as f:
        lines = f.readlines()
    
    header_end = 0
    for i, line in enumerate(lines):
        if 'endheader' in line.lower():
            header_end = i + 1
            break
    
    # Read the data starting after "endheader"
    # The next line contains column names
    df = pd.read_csv(sto_path, sep='\t', skiprows=header_end, skipinitialspace=True)
    
    return df


def extract_columns_to_2d(df, column_names):
    """
    Extract specific columns from DataFrame and return as 2D numpy array.
    
    Args:
        df: pandas DataFrame
        column_names: list of column names to extract
        
    Returns:
        2D numpy array of shape (n_rows, n_columns)
    """
    return df[column_names].values


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == '__main__':
    # Path to your .sto file
    sto_file = "/Users/adriananietocarrasco/Documents/Python IMU/MoBL_ARMS_Upper_Limb_Model_OpenSim_StaticOptimization_activation.sto"
    
    # Read the file
    print("Reading .sto file...")
    df = read_sto_file(sto_file)
    
    print(f"\nAvailable columns: {list(df.columns)}")
    print(f"Number of rows: {len(df)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    # ---- EXAMPLE 1: Extract a single column as 1D vector ----
    time_vector = df['time'].values
    print(f"\n--- Example 1: Single column ---")
    print(f"Time vector shape: {time_vector.shape}")
    print(f"First 5 values: {time_vector[:5]}")
    
    # ---- EXAMPLE 2: Extract 2 columns as 2D vector ----
    # Extract time and SUP columns
    columns_to_extract = ['time', 'SUP']
    vec_2d = extract_columns_to_2d(df, columns_to_extract)
    
    print(f"\n--- Example 2: Two columns (time, SUP) ---")
    print(f"2D vector shape: {vec_2d.shape}")  # (n_rows, 2)
    print(f"First 5 rows:")
    print(vec_2d[:5])
    
    # ---- EXAMPLE 3: Extract multiple muscle columns as 2D vector ----
    muscle_columns = ['SUP', 'ECRL', 'ECRB', 'ECU', 'FCR', 'FCU', 'PQ']
    muscle_data = extract_columns_to_2d(df, muscle_columns)
    
    print(f"\n--- Example 3: All muscle columns ---")
    print(f"Muscle data shape: {muscle_data.shape}")  # (n_rows, 7)
    print(f"First 3 rows:")
    print(muscle_data[:3])
    
    # ---- EXAMPLE 4: Extract specific muscles (e.g., FCR and FCU) ----
    specific_muscles = ['FCR', 'FCU']
    fcr_fcu_data = df[specific_muscles].values
    
    print(f"\n--- Example 4: FCR and FCU only ---")
    print(f"Shape: {fcr_fcu_data.shape}")
    print(f"First 5 rows:")
    print(fcr_fcu_data[:5])
    
    # ---- EXAMPLE 5: Alternative using numpy directly (without pandas) ----
    print(f"\n--- Example 5: Using numpy only (no pandas) ---")
    
    # Find header
    with open(sto_file, 'r') as f:
        lines = f.readlines()
    
    header_end = 0
    for i, line in enumerate(lines):
        if 'endheader' in line.lower():
            header_end = i + 1
            break
    
    # Read column names
    col_names = lines[header_end].strip().split('\t')
    col_names = [c.strip() for c in col_names]
    print(f"Column names: {col_names}")
    
    # Load data with numpy
    data = np.loadtxt(sto_file, skiprows=header_end+1)
    print(f"Data shape: {data.shape}")
    
    # Extract specific columns by index
    # time is column 0, SUP is column 1
    time_sup_numpy = data[:, [0, 1]]  # columns 0 and 1
    print(f"time + SUP shape: {time_sup_numpy.shape}")
    print(f"First 5 rows:")
    print(time_sup_numpy[:5])
    
    # Extract FCR (column 5) and FCU (column 6)
    fcr_fcu_numpy = data[:, [5, 6]]
    print(f"\nFCR + FCU shape: {fcr_fcu_numpy.shape}")
    print(f"First 5 rows:")
    print(fcr_fcu_numpy[:5])
    
    # ============================================================
    # PLOTTING: All muscles vs time
    # ============================================================
    
    print("\n" + "="*60)
    print("PLOTTING MUSCLE ACTIVATIONS")
    print("="*60)
    
    # Get time and all muscle columns
    time = df['time'].values
    muscles = ['ECRL', 'FCR', 'SUP', 'ECU', 'FCU', 'PQ']
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    fig.suptitle('Muscle Activations Over Time', fontsize=16, fontweight='bold')
    
    # Flatten axes for easy iteration
    axes = axes.flatten()
    
    # Plot each muscle
    for idx, muscle in enumerate(muscles):
        ax = axes[idx]
        activation = df[muscle].values
        
        ax.plot(time, activation, linewidth=1.5, color='steelblue')
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Activation', fontsize=10)
        ax.set_title(f'{muscle}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, max(activation) * 1.1])  # Add 10% padding at top
    
    plt.tight_layout()
    
    # Save the figure
    output_path = "/Users/adriananietocarrasco/Documents/Python IMU/muscle_activations_plot.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_path}")
    
    # Show the plot
    plt.show()
    
    # ============================================================
    # BONUS: All muscles on one plot
    # ============================================================
    
    fig2, ax2 = plt.subplots(figsize=(14, 6))
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for idx, muscle in enumerate(muscles):
        activation = df[muscle].values
        ax2.plot(time, activation, label=muscle, linewidth=2, color=colors[idx], alpha=0.8)
    
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Activation', fontsize=12)
    ax2.set_title('All Muscle Activations vs Time', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the combined plot
    output_path2 = "/Users/adriananietocarrasco/Documents/Python IMU/muscle_activations_combined.png"
    plt.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"Combined plot saved to: {output_path2}")
    
    plt.show()
    
    # ============================================================
    # ECRL and FCR only
    # ============================================================
    
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    
    # Plot ECRL and FCR
    ecrl_data = df['ECRL'].values
    fcr_data = df['FCR'].values
    
    ax3.plot(time, ecrl_data, label='ECRL', linewidth=2, color='#e74c3c', alpha=0.8)
    ax3.plot(time, fcr_data, label='FCR', linewidth=2, color='#3498db', alpha=0.8)
    
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Activation', fontsize=12)
    ax3.set_title('ECRL and FCR Muscle Activations vs Time', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the ECRL-FCR plot
    output_path3 = "/Users/adriananietocarrasco/Documents/Python IMU/muscle_activations_ECRL_FCR.png"
    plt.savefig(output_path3, dpi=300, bbox_inches='tight')
    print(f"ECRL-FCR plot saved to: {output_path3}")
    
    plt.show()
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
