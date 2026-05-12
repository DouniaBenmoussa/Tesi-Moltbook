import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

from Analisi import G

# Si recupera il nodo numero 1 in classifica
top_path = r"/data3/dbenmoussa/risultati/Classifica_Top_Nodi.csv"
print(f"Loading Top nodes from: {top_path}")

try:
    df_top = pd.read_csv(top_path, sep=';', decimal=',')
except FileNotFoundError:
    print("Error: File not found")
    exit()

# Si recupera l'ID del nodo e il suo PageRank
top_node_id = df_top.iloc[0]['agent_id']
top_pagerank = df_top.iloc[0]['pagerank']
print(f"The top node is: {top_node_id} (PageRank: {top_pagerank})")

# Si costruisce l'ego-graph del nodo top per visualizzare le sue connessioni dirette
print("Building the Ego-Graph...")

ego_net = nx.ego_graph(G, top_node_id, radius=1, undirected=True)
print(f"The ego-graph has {ego_net.number_of_nodes()} nodes and {ego_net.number_of_edges()} edges")

# Si disegna il grafo
print("Drawing the graph...")
plt.figure(figsize=(14, 14))

# Si posizionano i nodi
pos = nx.spring_layout(ego_net, k=0.15, seed=42)

# Si disegnano i nodi
neighbor = [n for n in ego_net.nodes() if n != top_node_id]
nx.draw_networkx_nodes(ego_net, pos, nodelist=neighbor, node_color='cornflowerblue', node_size=40, alpha=0.6)
nx.draw_networkx_nodes(ego_net, pos, nodelist=[top_node_id], node_color='crimson', node_size=600, edgecolors='black', linewidths=2)

# Si disegnano gli archi
nx.draw_networkx_edges(ego_net, pos, width=0.3, alpha=0.3, edge_color='gray')

plt.title(f"Ego-Nework del Nodo più influente (Rank #1)\nID: {top_node_id}", fontsize=18, fontweight='bold')
plt.axis('off')

# Si salva il grafico nella cartella dei grafici
dest_fold = "/data3/dbenmoussa/grafici"
os.makedirs(dest_fold, exist_ok=True)
rm_path = os.path.join(dest_fold, "Ego_Graph_Top_Nodo.png")

plt.savefig(rm_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Grafo salvato in: {rm_path}")
