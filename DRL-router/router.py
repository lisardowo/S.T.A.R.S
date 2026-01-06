import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import simpy
import formulas
import consideraciones
import random
from satelites import ConstellationManager
import monitor
import time

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
    def __init__(self, constellation_manager, model_dir="DRL-router/mejorModelo", model_name="best_model.pth", train_mode=True):
        self.constellation = constellation_manager
        self.model_dir = model_dir
        self.model_name = model_name
        self.model_path = os.path.join(self.model_dir, self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.train_mode = train_mode  # New parameter to control training mode

        self.input_dim = 4 
        self.hidden_dim = 64
        self.agent = GMTS_Agent(self.input_dim, self.hidden_dim).to(self.device)

        if self.train_mode:
            self.optimizer = torch.optim.Adam(self.agent.parameters(), lr=0.001)
            self.trainer = SatelliteTrainer(self.agent, self.optimizer)
            self.best_reward = -float('inf')

        # Ensure the model directory exists
        os.makedirs(self.model_dir, exist_ok=True)

        if os.path.exists(self.model_path):
            self.agent.load_state_dict(torch.load(self.model_path))
            print(f"[*] Modelo cargado desde {self.model_path}")

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
        if self.train_mode and current_reward > self.best_reward:
            self.best_reward = current_reward
            torch.save(self.agent.state_dict(), self.model_path)
            
            return True
        return False

# --- BUCLE DE ENTRENAMIENTO PRINCIPAL ---
if __name__ == "__main__":
    env = simpy.Environment()
    constellation = ConstellationManager(env)

    # --- Dentro de if __name__ == "__main__": ---
    history = {
    'epochs': [],
    'rewards': [],
    'throughputs': []
    }

    # Set train_mode to False for inference
    train_mode = True  # Change to False to disable training

    router = IntelligentRouter(constellation, model_dir="DRL-router/mejorModelo", train_mode=train_mode)

    if train_mode:
        print("\n[*] Iniciando Entrenamiento DRL...")
        for epoch in range(1000):
            initialTime = time.time()
            # Procedural simulation step
            env.run(until=env.now + 1)

            # Generar valores aleatorios para src_p, src_s, dst_p, dst_s
            N_P, N_S = constellation.planes, constellation.sats_per_plane
            src_p, src_s = random.randint(0, N_P-1), random.randint(0, N_S-1)
            dst_p, dst_s = random.randint(0, N_P-1), random.randint(0, N_S-1)
            log_file = "drl_benchmark_log.txt"
            # Get router decision
            candidates, ratios, value = router.find_best_routes(0, 0, 3, 5)

            if candidates:
                # Train and get reward
                reward = router.trainer.train_step(ratios, value, candidates)
            # Monitor resources
                avg_tp = sum([c['throughput'] for c in candidates]) / len(candidates)
                avg_delay = sum([c['delay'] for c in candidates]) / len(candidates)
                max_load = max([c['max_load'] for c in candidates])
                ratios_np = ratios.detach().cpu().numpy().round(3).tolist()
               
            #graph arrays

                history['epochs'].append(epoch)
                history['rewards'].append(reward)
                history['throughputs'].append(avg_tp)
            

                # Save best model
                is_best = router.save_if_best(reward)

                #debug log
             
                debug_data = {
                'epoch': epoch,
                'reward': reward,
                'is_best': is_best,
                'tp': avg_tp,
                'delay': avg_delay,
                'src': f"P{src_p}S{src_s}",
                'dst': f"P{dst_p}S{dst_s}",
                'ratios': ratios_np,
                'max_load': max_load,
                'exec_time': time.time() - initialTime
                }
                #log
                monitor.log_epoch_stats(log_file, debug_data)



                if epoch % 10 == 0:
                    status = "[NUEVO MEJOR]" if is_best else ""
                    print(f"Epoch {epoch:03d} | Reward: {reward:.4f} | Ratios: {ratios.detach().cpu().numpy().round(2)} {status}")
        
        print("\n[*] Entrenamiento completado. El mejor modelo se guardó en 'best_model.pth'")
        print("\n[*] Activity Log Generado")
        monitor.plot_training_results(history['epochs'], history['rewards'], history['throughputs'])

    else:
        print("\n[*] Usando el modelo entrenado para inferencia...")
        # Example of using the model for inference
        candidates, ratios, value = router.find_best_routes(0, 0, 3, 5)
        print(f"[*] Candidatos: {candidates}")