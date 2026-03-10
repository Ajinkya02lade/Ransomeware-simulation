import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

# --- Settings ---
NUM_NODES = 80
PROB_INFECT = 0.25   # Natural spread rate
PROB_RECOVER = 0.05  # Slow manual patching
KILL_SWITCH_THRESHOLD = 0.20  # Trigger if 20% of nodes are infected
STEPS = 60

# 1. Initialize Network
G = nx.barabasi_albert_graph(NUM_NODES, 2) # Scale-free network (hubs)
pos = nx.spring_layout(G, seed=42)
states = {node: 0 for node in G.nodes()} # 0:Safe, 1:Infected, 2:Recovered

# Start Patient Zero
patient_zero = random.choice(list(G.nodes()))
states[patient_zero] = 1

fig, (ax_net, ax_graph) = plt.subplots(1, 2, figsize=(16, 6))
history = {'I': [1], 'S': [NUM_NODES-1], 'R': [0]}
kill_switch_activated = False

def update(frame):
    global states, PROB_INFECT, kill_switch_activated
    
    # --- Logic ---
    current_infected = sum(1 for s in states.values() if s == 1)
    infection_ratio = current_infected / NUM_NODES
    
    # Trigger Kill Switch
    if infection_ratio >= KILL_SWITCH_THRESHOLD and not kill_switch_activated:
        kill_switch_activated = True
        PROB_INFECT = 0.02 # Drastically reduce spread (Isolation)

    new_states = states.copy()
    for node in G.nodes():
        if states[node] == 0:
            neighbors = list(G.neighbors(node))
            if any(states[n] == 1 for n in neighbors) and random.random() < PROB_INFECT:
                new_states[node] = 1
        elif states[node] == 1:
            if random.random() < PROB_RECOVER:
                new_states[node] = 2
    
    states = new_states
    
    # Update Stats for the line graph
    s_c = sum(1 for s in states.values() if s == 0)
    i_c = sum(1 for s in states.values() if s == 1)
    r_c = sum(1 for s in states.values() if s == 2)
    history['S'].append(s_c)
    history['I'].append(i_c)
    history['R'].append(r_c)

    # --- Drawing ---
    ax_net.clear()
    colors = ['#2ecc71' if states[n]==0 else '#e74c3c' if states[n]==1 else '#3498db' for n in G.nodes()]
    nx.draw(G, pos, ax=ax_net, node_color=colors, node_size=200, edge_color='#ecf0f1', width=0.5)
    
    status_text = "KILL SWITCH ACTIVE" if kill_switch_activated else "MONITORING..."
    ax_net.set_title(f"Step {frame} | {status_text}", color='red' if kill_switch_activated else 'black')

    ax_graph.clear()
    ax_graph.plot(history['I'], color='red', label='Infected')
    ax_graph.plot(history['S'], color='green', label='Vulnerable')
    ax_graph.plot(history['R'], color='blue', label='Recovered')
    ax_graph.set_title("Real-time Stats")
    ax_graph.legend(loc='upper right')

ani = FuncAnimation(fig, update, frames=STEPS, interval=300, repeat=False)
plt.tight_layout()
plt.show()