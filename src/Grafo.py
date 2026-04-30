import networkx as nx
import matplotlib.pyplot as plt
import random

from Analisi import G

print("\nGenerating a random graph...")

possible_nodes = []

for node in G.nodes():
    # Raccogliamo tutti gli utenti unici che gli hanno scritto o a cui ha scritto
    neighbors = set(G.predecessors(node)).union(set(G.successors(node)))
    neighbors.discard(node) # Ignoriamo se stesso (i self-loop) per questo conteggio
    
    # Si vogliono nodi che abbiano tra 5 e 15 vicini (esclusi i self-loop) per avere un grafo di dimensione media
    if 5 <= len(neighbors) <= 15:
        possible_nodes.append(node)

# Si prende un nodo a caso tra quelli validi
central_node = random.choice(possible_nodes)

# Si estrae e ordina il sotto-grafo con raggio 1 attorno al nodo centrale
# undirected=True permette di includere sia i mittenti che i destinatari del nodo centrale
mini_G = nx.ego_graph(G, central_node, radius=1, undirected=True)

print(f"Central node chosen: {central_node[:8]}... (The graph will contain {mini_G.number_of_nodes()} nodes)")

# Si trovano le frecce che non partono/arrivano al centro
peripheral_arches = [edge for edge in mini_G.edges() if central_node not in edge]

# Si mettono in fila prima i nodi che hanno legami periferici tra loro, in modo che finiscano vicini
interconnected_nodes = []
for sender, receiver in peripheral_arches:
    if sender not in interconnected_nodes: interconnected_nodes.append(sender)
    if receiver not in interconnected_nodes: interconnected_nodes.append(receiver)

# Si recuperano tutti gli altri nodi periferici "solitari"
other_nodes = [n for n in mini_G.nodes() if n != central_node and n not in interconnected_nodes]

# Si uniscono le liste: prima le coppiette, poi gli altri
ordered_peripheral_nodes = interconnected_nodes + other_nodes

# Si creano i due strati passando la lista ORDINATA
layers = [[central_node], ordered_peripheral_nodes]
positions = nx.shell_layout(mini_G, nlist=layers)

# Si preparano le etichette
short_labels = {node: str(node)[:6] + "..." for node in mini_G.nodes()}

plt.figure(figsize=(13, 11))

# Disegno del grafo base
nx.draw(mini_G, pos=positions, labels=short_labels, node_color='#87CEFA', node_size=2500, edge_color='gray', font_size=10, font_weight='bold', arrows=True, arrowsize=20)

custom_edge_labels = {}

for u, v, data in mini_G.edges(data=True):
    if u == v: # Si ignorano i self-loop per non sovrapporli al nodo
        continue
        
    weight = data['weight']
    
    # Si controlla se c'è un'interazione reciproca
    if mini_G.has_edge(v, u):
        weight_return = mini_G[v][u]['weight']
        
        # Si uniscono i due pesi con un simbolo di scambio (es. 2 ⇅ 5).
        if str(u) < str(v): 
            custom_edge_labels[(u, v)] = f"{weight} ⇅ {weight_return}"
    else:
        # Se è a senso unico, stampiamo il numero normalmente
        custom_edge_labels[(u, v)] = str(weight)

# Si disegnano i pesi (saltando i self loop)
nx.draw_networkx_edge_labels(mini_G, pos=positions, edge_labels=custom_edge_labels, font_color='red', font_size=12, font_weight='bold', label_pos=0.5)

ax = plt.gca()
ax.margins(x=0.2, y=0.4) 

y_min, y_max = ax.get_ylim()
height = y_max - y_min
offset_y = height * 0.08 if height > 0.1 else 0.2

for node in mini_G.nodes():
    if mini_G.has_edge(node, node):
        weight_self = mini_G[node][node]['weight']
        x, y = positions[node]
        
        # Si posiziona il peso in alto con lo sfondino bianco per renderlo leggibile
        plt.text(x, y + offset_y, str(weight_self), color='red', fontsize=14, fontweight='bold', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))

plt.title(f"Random Graph (Center: {central_node[:8]}...)", fontsize=15, fontweight='bold')
plt.show()