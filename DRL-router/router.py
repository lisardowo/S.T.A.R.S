import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import simpy
import formulas
import consideraciones
from satellites import ConstellationManager

# --- AGENTE DRL ---
class GMTS_Agent(nn.Module):
    def __init__(self, input_dim, hidden_dim, L=3):
        super(GMTS_Agent, self).__init__()
        self.gnn_layer = nn.Linear(input_dim, hidden_dim)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, L),
            nn.Softmax(dim=-1) 
        )
        self.critic = nn.Linear(hidden_dim, 1)

    def forward(self, state_features):
        x = F.relu(self.gnn_layer(state_features))
        global_repr = torch.mean(x, dim=0) 
        return self.actor(global_repr), self.critic(global_repr)

# --- ENTRENADOR (Logic de Recompensa y Optimización) ---
class SatelliteTrainer:
    def __init__(self, agent, optimizer, beta1=0.5):
        self.agent = agent
        self.optimizer = optimizer
        self.beta1 = beta1

    def train_step(self, ratios, value, augmented_candidates):
        """Calcula la utilidad y actualiza la red neuronal."""
        # Extraer métricas de los candidatos para la función de entrenamiento
        avg_throughput = sum([c['throughput'] for c in augmented_candidates]) / len(augmented_candidates)
        avg_delay = sum([c['delay'] for c in augmented_candidates]) / len(augmented_candidates)
        
        # Calcular Recompensa (Utility) usando consideraciones.py
        reward = consideraciones.TrainingFunction(avg_throughput, avg_delay, self.beta1)
        reward_tensor = torch.tensor([reward], dtype=torch.float32).to(value.device)
        
        # Loss de Actor-Critic
        advantage = reward_tensor - value.detach()
        loss_actor = -torch.log(ratios).mean() * advantage
        loss_critic = F.mse_loss(value, reward_tensor)
        
        total_loss = loss_actor + loss_critic
        
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()
        
        return reward

# --- CLASE BRIDGE: ROUTER INTELIGENTE ---
class IntelligentRouter:
    def __init__(self, constellation_manager, model_path="best_model.pth"):
        self.constellation = constellation_manager
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.input_dim = 4 
        self.hidden_dim = 64
        self.agent = GMTS_Agent(self.input_dim, self.hidden_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.agent.parameters(), lr=0.001)
        self.trainer = SatelliteTrainer(self.agent, self.optimizer)
        self.best_reward = -float('inf')

        if os.path.exists(model_path):
            self.agent.load_state_dict(torch.load(model_path))
            print(f"[*] Modelo cargado desde {model_path}")

    def _calculate_formulas_inputs(self, src_plane, src_sat, dst_plane, dst_sat):
        N_P, N_S = self.constellation.planes, self.constellation.sats_per_plane
        raan_delta = formulas.RAAN_Delta(src_plane * (2*math.pi/N_P), dst_plane * (2*math.pi/N_P))
        hops_h = formulas.eastANDwest_Hops(raan_delta, N_P)
        p_delta = formulas.phaseDelta(N_S, N_P, 1)
        e_lat, w_lat = formulas.phaseAngleNormalization(dst_sat*(2*math.pi/N_S), src_sat*(2*math.pi/N_S), hops_h['east'], hops_h['west'], p_delta)
        return hops_h, formulas.CardinalDirectionsHops(e_lat, w_lat, N_S)

    def _extract_path_metrics(self, path_links):
        total_q, total_r, dists, traffics, loads = 0, 0, [], [], []
        for link in path_links:
            u, v = link.split('-')
            m = self.constellation.get_link_metrics(u, v)
            total_q += m['q_delay']; total_r += m['r_delay']
            dists.append(m['distance']); traffics.append(m['link_traffic'])
            loads.append(self.constellation.satellites[v].current_load)
        
        return {
            'delay': consideraciones.PathDelay([total_q], [total_r], [sum(dists)]),
            'throughput': consideraciones.PathThroughput(traffics),
            'max_load': max(loads) if loads else 0
        }

    def find_best_routes(self, src_p, src_s, dst_p, dst_s):
        h_h, h_v = self._calculate_formulas_inputs(src_p, src_s, dst_p, dst_s)
        candidates = formulas.GetOptimalPaths(src_s, src_p, h_h, h_v, self.constellation.sats_per_plane, self.constellation.planes)
        
        if not candidates: return None, None, None

        features, augmented = [], []
        for cand in candidates:
            m = self._extract_path_metrics(cand['enlaces'])
            features.append([cand['hops']/10.0, m['delay']*10.0, m['throughput']/1000.0, m['max_load']])
            cand.update(m); augmented.append(cand)

        state_tensor = torch.tensor(features, dtype=torch.float32).to(self.device)
        ratios, value = self.agent(state_tensor)
        return augmented, ratios, value

    def save_if_best(self, current_reward):
        if current_reward > self.best_reward:
            self.best_reward = current_reward
            torch.save(self.agent.state_dict(), self.model_path)
            return True
        return False

# --- BUCLE DE ENTRENAMIENTO PRINCIPAL ---
if __name__ == "__main__":
    env = simpy.Environment()
    constellation = ConstellationManager(env)
    router = IntelligentRouter(constellation)
    
    print("\n[*] Iniciando Entrenamiento DRL...")
    for epoch in range(100):
        # Avanzar simulación procedural
        env.run(until=env.now + 1)
        
        # Obtener decisión del router
        candidates, ratios, value = router.find_best_routes(0, 0, 3, 5)
        
        if candidates:
            # Entrenar y obtener recompensa
            reward = router.trainer.train_step(ratios, value, candidates)
            
            # Guardar mejor modelo
            is_best = router.save_if_best(reward)
            
            if epoch % 10 == 0:
                status = "[NUEVO MEJOR]" if is_best else ""
                print(f"Epoch {epoch:03d} | Reward: {reward:.4f} | Ratios: {ratios.detach().cpu().numpy().round(2)} {status}")

    print("\n[*] Entrenamiento completado. El mejor modelo se guardó en 'best_model.pth'")