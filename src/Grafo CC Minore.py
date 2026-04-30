import networkx as nx
import matplotlib.pyplot as plt
import random

from Analisi import G

print("\nConnected Component Analysis...")

# Si trovano tutte le isole (WCC)
wcc = list(nx.weakly_connected_components(G))

# Si trova qual è la dimensione minima in assoluto tra tutte le componenti (WCC)
min_dim = min(len(c) for c in wcc)

# Si raccolgono tutte le componenti che hanno esattamente quella dimensione
all_small = [c for c in wcc if len(c) == min_dim]

# Se ne pescano una a caso ogni volta che si avvia il codice (per non disegnare sempre la stessa componente più piccola)
small_comp = random.choice(all_small)

# Si crea il sotto-grafo
g_small = G.subgraph(small_comp).copy()

print(f"The smallest component found has {g_small.number_of_nodes()} nodes")

# Disegno del grafico della componente più piccola
plt.figure(figsize=(10, 8))
plt.title(f"Graph of the smallest connected component\n({g_small.number_of_nodes()} nodes)", fontsize=18, pad=20)

pos = nx.spring_layout(g_small, seed=42)
labels = {n: str(n)[:6] + "..." for n in g_small.nodes()}

nx.draw(g_small, pos, labels=labels, with_labels=True, node_color='lightgreen', node_size=3000, edge_color='gray', font_size=12, font_weight='bold', arrows=True, arrowsize=20)

custom_edge_labels = {}
for u, v, data in g_small.edges(data=True):
    if u == v:     # Si ignorano i self-loop per non sovrapporli al nodo
        continue
        
    weight = data['weight']
    
    # Si controlla se c'è un'interazione reciproca
    if g_small.has_edge(v, u):
        if str(u) < str(v): 
            weight_return = g_small[v][u]['weight']
            custom_edge_labels[(u, v)] = f"{weight} ⇅ {weight_return}"
    else:
        custom_edge_labels[(u, v)] = str(weight)

# Si disegnano le etichette degli archi con i pesi
nx.draw_networkx_edge_labels(g_small, pos, edge_labels=custom_edge_labels, font_color='red', font_size=14)

ax = plt.gca()
if g_small.number_of_nodes() == 1:
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    ax.set_xlim(x_min - 0.2, x_max + 0.2)
    ax.set_ylim(y_min - 0.2, y_max + 0.5)
else:
    ax.margins(x=0.2, y=0.4)

y_min, y_max = ax.get_ylim()
offset_y = (y_max - y_min) * 0.08

for node in g_small.nodes():
    if g_small.has_edge(node, node):
        weight = g_small[node][node]['weight']
        x, y = pos[node]
        
        plt.text(x, y + offset_y, str(weight), color='red', fontsize=16, fontweight='bold', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))

plt.show()