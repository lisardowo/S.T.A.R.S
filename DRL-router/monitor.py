import matplotlib.pyplot as plt
import os
def plot_training_results(epochs, rewards, throughputs):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Eje para la Recompensa
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Reward', color='tab:blue')
    ax1.plot(epochs, rewards, color='tab:blue', label='Reward')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Eje para el Throughput
    ax2 = ax1.twinx()
    ax2.set_ylabel('Avg Throughput', color='tab:red')
    ax2.plot(epochs, throughputs, color='tab:red', linestyle='--', label='Throughput')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Progreso del Entrenamiento DRL')
    fig.tight_layout()
    plt.show()

    

def log_epoch_stats(file_path, data):
    """
    Registra las estadísticas de la época en un archivo de texto.
    Data debe ser un diccionario con las llaves correspondientes.
    """
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, "a") as f:
        # Escribir cabecera si el archivo es nuevo
        if not file_exists:
            header = ("Epoch\tReward\tBest?\tAvg_TP\tAvg_Delay\tSrc\tDst\t"
                     "Ratios(W/E/S)\tMax_Load\tExecution_Time\n")
            f.write(header)
        
        # Formatear los datos en columnas
        line = (
            f"{data['epoch']}\t"
            f"{data['reward']:.4f}\t"
            f"{'[NUEVO MEJOR]' if data['is_best'] else '-'}\t"
            f"{data['tp']:.2f}\t"
            f"{data['delay']:.4f}\t"
            f"{data['src']}\t"
            f"{data['dst']}\t"
            f"{data['ratios']}\t"
            f"{data['max_load']:.2f}\t"
            f"{data['exec_time']:.4f}\n"
        )
        f.write(line)
        