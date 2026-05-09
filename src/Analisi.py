from datasets import load_dataset
import networkx as nx
import pandas as pd


# Il mio token di accesso a Hugging Face
my_token = "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"

# Definizione del nome del dataset da scaricare
DATASET_NAME = "SimulaMet/moltbook-observatory-archive"

print("Downloading dataset...")

# Si scaricano i tre dataset (agents, comments, posts) dalla piattaforma Hugging Face utilizzando la funzione load_dataset
dataset_agents = load_dataset(DATASET_NAME, "agents", split="archive", token=my_token)
dataset_comments = load_dataset(DATASET_NAME, "comments", split="archive", token=my_token)
dataset_posts = load_dataset(DATASET_NAME, "posts", split="archive", token=my_token)

# Si convertono i dataset in DataFrame di Pandas per facilitare l'analisi e la manipolazione dei dati
df_agents = dataset_agents.to_pandas()
df_comments = dataset_comments.to_pandas()
df_posts = dataset_posts.to_pandas()

print("Data downloaded and converted successfully in Pandas DataFrame")
print(f"Number of agents: {len(df_agents)} | Number of comments: {len(df_comments)} | Number of posts: {len(df_posts)}")

# Si dividono i commenti in due gruppi in base alla colonna parent_id, per definire se commento a post o commento ad un'altro commento
post_comments = df_comments[df_comments['parent_id'].isna()]
comments_reply = df_comments[df_comments['parent_id'].notna()]

# Interazione 1: chi commenta -> chi ha scritto il post
interactions_posts = pd.merge(post_comments[['agent_id', 'post_id']], df_posts[['id', 'agent_id']], left_on='post_id', right_on='id', suffixes=('_sender', '_receiver'))[['agent_id_sender', 'agent_id_receiver']]

# Interazione 2: chi risponde con un commento -> chi ha scritto il commento originale (si va a fare una self-join sul dataset comments)
interactions_comments = pd.merge(comments_reply[['agent_id', 'parent_id']], df_comments[['id', 'agent_id']], left_on='parent_id', right_on='id', suffixes=('_sender', '_receiver'))[['agent_id_sender', 'agent_id_receiver']]

# Si uniscono le due tabelle di Interazione 1 e Interazione 2, mettendole una sopra l'altra (con colonne agent_id_sender e agent_id_receiver) in modo da ottenere un'unica grande tabella
total_interactions = pd.concat([interactions_posts, interactions_comments])

# Si raggruppano le coppie di agenti e si contano quante interazioni ci sono state tra loro
weighted_edge = total_interactions.groupby(['agent_id_sender', 'agent_id_receiver']).size().reset_index(name='weight')

print("Building the topology of the Directed Graph...")

# Si crea il grafo con i nodi che hanno almeno un arco partendo dal DataFrame weightes_edge
G = nx.from_pandas_edgelist(weighted_edge, source='agent_id_sender', target='agent_id_receiver', edge_attr='weight', create_using=nx.DiGraph())

# Vengono aggiunti anche i nodi "isolati" (agenti che non hanno mai interagito) al grafo
G.add_nodes_from(df_agents['id'])

# Viene fatta una mappatura degli attributi (karma) ai relativi nodi (agenti) e reso il tutto un dizionario
karma_dict = dict(zip(df_agents['id'], df_agents['karma']))

# Si applica il dizionario a tutto il grafo in modo da assegnare gli attributi ai relativi nodi
nx.set_node_attributes(G, karma_dict, 'karma')

print("Operation successfully done")
print(f"Total number of Nodes (Agents): {G.number_of_nodes()}")
print(f"Total number of Edges (Unique Interactions): {G.number_of_edges()}")

print("Analyzing Components...")

# Si trovano tutte le componenti debolmente connesse (WCC)
wcc = list(nx.weakly_connected_components(G))
num_wcc = len(wcc)
print(f"The network is divided in {num_wcc} distinct isle (WCC)")

# Si trova la componente più grande (Giant Component) tra le WCC e si calcola la percentuale di nodi che contiene rispetto al totale del grafo
giant_component_wcc = max(wcc, key=len)
giant_nodes = len(giant_component_wcc)
giant_perc = (giant_nodes / G.number_of_nodes()) * 100
print(f"The giant component WCC has {giant_nodes} agents ({giant_perc:.2f}% of the total)")

# Si trovano tutte le componenti fortemente connesse (SCC)
scc = list(nx.strongly_connected_components(G))
num_scc = len(scc)
print(f"The network is divided in {num_scc} strongly connected components (SCC)")

# Si trova la componente più grande tra le SCC
giant_component_scc = max(scc, key=len)
print(f"The giant component SCC has {len(giant_component_scc)} agents")

# Si calcola il coefficiente di clustering globale del grafo
print("Calculating the global clustering coefficient...")
glb_clustering = nx.transitivity(G)
print(f"Global Clustering Coefficient: {glb_clustering:.4f}")
