import matplotlib.pyplot as plt

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