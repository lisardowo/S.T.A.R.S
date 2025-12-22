import torch
import torch.nn as nn
import torch.nn.functional as F
from formulas import GetOptimalPaths
from consideraciones import TrainingFunction, PathDelay, PathThroughput, getAdjascencyMatrix, getNetworkState 

class GMTS_Agent(nn.Module):
    def __init__(self, input_dim, hidden_dim, L=3):
        super(GMTS_Agent, self).__init__()
        # Procesamiento de características de nodos y enlaces
        self.gnn_layer = nn.Linear(input_dim, hidden_dim)
        
        # Actor: Genera la distribución de tráfico para las L rutas (Ecuación 2)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, L),
            nn.Softmax(dim=-1) 
        )
        
        # Critic: Estima la utilidad (Recompensa esperada)
        self.critic = nn.Linear(hidden_dim, 1)

    def forward(self, state_features, adj_matrix):
        # Paso de mensajes GNN simple
        x = F.relu(torch.matmul(adj_matrix, self.gnn_layer(state_features)))
        global_repr = torch.mean(x, dim=0)
        
        ratios = self.actor(global_repr) # Vector omega [w1, w2, w3]
        value = self.critic(global_repr)
        return ratios, value

class SatelliteTrainer:
    def __init__(self, model, optimizer, beta1=0.5):
        self.model = model
        self.optimizer = optimizer
        self.beta1 = beta1 # Balance entre Throughput y Delay (Ecuación 6)

    def compute_network_metrics(self, routes_data, traffic_ratios):
        """
        Integra consideraciones.py para evaluar la decisión de la IA.
        """
        path_delays: list = []
        path_throughputs : list = []

        for i, route in enumerate(routes_data):
            # 1. Calcular Retraso de la Ruta (Ecuación 1)
            # En un entorno real, estos datos vendrían del simulador (ej. NS3)
            delay: float = PathDelay(route['q_delays'], route['r_delays'], route['distances'])
            path_delays.append(delay)

            # 2. Calcular Throughput de la Ruta (Ecuación 5)
            # Escalado por el ratio (omega) decidido por la IA
            throughput = PathThroughput(route['link_traffics']) * traffic_ratios[i].item()
            path_throughputs.append(throughput)

        avg_f = sum(path_throughputs) / len(path_throughputs)
        avg_d = sum(path_delays) / len(path_delays)
        
        return avg_f, avg_d

    def train_step(self, state, adj, candidate_routes):
        self.optimizer.zero_grad()
        
        # 1. La IA decide los ratios de tráfico (omega)
        ratios, value = self.model(state, adj)
        
        # 2. Evaluación física usando consideraciones.py
        avg_f, avg_d = self.compute_network_metrics(candidate_routes, ratios)
        
        # 3. Cálculo de Recompensa/Utilidad (Ecuación 6)
        reward = TrainingFunction(avg_f, avg_d, self.beta1)
        
        # 4. Cálculo de pérdida (PPO/Policy Gradient simplificado)
        # Buscamos maximizar la recompensa (minimizar -reward)
        advantage = reward - value.item()
        loss_actor = -torch.log(ratios).mean() * advantage
        loss_critic = F.mse_loss(value, torch.tensor([reward]))
        
        total_loss = loss_actor + loss_critic
        total_loss.backward()
        self.optimizer.step()
        
        return reward



# Inicialización
trainer = SatelliteTrainer(agent,optimizer , beta1=0.6)
MAX_EPOCHS = 500
sourceSatelite =  
sourcePlane = 
h_hops_dict = 
v_hops_dict = 
NumberSatelites = 11
NumberPlanes = 6
for epoch in range(MAX_EPOCHS):
    # FASE 1: Descubrimiento de rutas (formulas.py)
    # Obtenemos las L mejores rutas físicas
    rutas_IA = GetOptimalPaths(
        sourceSatelite, sourcePlane, 
        h_hops_dict, v_hops_dict, 
        NumberSatelites, NumberPlanes
    )

    # FASE 2: Entrenamiento (consideraciones.py + PyTorch)
    # 'rutas_IA' ahora contiene los 'enlaces' que la IA debe evaluar
    state_tensor = getNetworkState(rutas_IA) # Datos de congestión actual
    adj_tensor = getAdjascencyMatrix(rutas_IA)
    
    reward = trainer.train_step(state_tensor, adj_tensor, rutas_IA)
    
    if epoch % 50 == 0:
        print(f"Epoch {epoch} | Recompensa (Utilidad): {reward:.4f}")