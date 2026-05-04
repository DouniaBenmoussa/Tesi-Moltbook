import pandas as pd
import networkx as nx
from datasets import load_dataset
import os

# Il mio token di accesso a Hugging Face
my_token = "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"

# Definizione del nome del dataset da scaricare
DATASET_NAME = "SimulaMet/moltbook-observatory-archive"

print("Downloading dataset...")
df_comments = load_dataset(DATASET_NAME, "comments", split="archive", token=my_token).to_pandas()
df_posts = load_dataset(DATASET_NAME, "posts", split="archive", token=my_token).to_pandas()

# Si definisce la data/ora esatta dello snapshot che ci interessa
print("Cumulative filtering up to snapshot date...")
snapshot_time = pd.to_datetime("2026-04-23T10:32:56.597852Z", utc=True)

# Si convertono le date di creazione nel corretto formato per fare il confronto
df_comments['created_at'] = pd.to_datetime(df_comments['created_at'], utc=True)
df_posts['created_at'] = pd.to_datetime(df_posts['created_at'], utc=True)

# Si tiene tutto lo storico accumulato fino a quel preciso istante
df_comments = df_comments[df_comments['created_at'] <= snapshot_time]
df_posts = df_posts[df_posts['created_at'] <= snapshot_time]

# Se ci sono salvataggi multipli dello stesso post/commento, si tiene solo la riga dell'ultimo dump
if 'dump_date' in df_posts.columns:
    df_posts = df_posts.sort_values('dump_date').drop_duplicates(subset=['id'], keep='last')
    df_comments = df_comments.sort_values('dump_date').drop_duplicates(subset=['id'], keep='last')
else:
    df_posts = df_posts.drop_duplicates(subset=['id'], keep='last')
    df_comments = df_comments.drop_duplicates(subset=['id'], keep='last')


# Creazione Grafo: si uniscono interazioni ai post e interazioni ai commenti
print("Construction of edges (interactions)...")
edges = pd.concat([
    df_comments[df_comments['parent_id'].isna()].merge(df_posts, left_on='post_id', right_on='id')[['agent_id_x', 'agent_id_y']],
    df_comments[df_comments['parent_id'].notna()].merge(df_comments, left_on='parent_id', right_on='id')[['agent_id_x', 'agent_id_y']]
]).rename(columns={'agent_id_x': 'source', 'agent_id_y': 'target'})

# Si rimuovono gli "autocommenti" per non sfalsare le metriche di centralità (es. utente che risponde a sé stesso)
edges = edges[edges['source'] != edges['target']]

# Si raggruppano i pesi e si crea la Componente Gigante del grafo
print("Building the graph...")
G_snap = nx.from_pandas_edgelist(edges.groupby(['source', 'target']).size().reset_index(name='w'), edge_attr='w', create_using=nx.DiGraph)

# Si assicura che il grafo non sia vuoto prima di cercare la componente gigante
if G_snap.number_of_nodes() > 0:
    g_giant = G_snap.subgraph(max(nx.weakly_connected_components(G_snap), key=len))
    print(f"Nodes in the analyzed giant network: {g_giant.number_of_nodes()}")

    print("\n--- START CALCULATION CENTRALITY ---")
    
    print("1/4 In-Degree Calculation...")
    in_deg = nx.in_degree_centrality(g_giant)
    
    print("2/4 PageRank Calculation...")
    pr = nx.pagerank(g_giant, weight='w')
    
    print("3/4 Betweenness Calculation...")
    betw = nx.betweenness_centrality(g_giant)
    
    print("4/4 Closeness Calculation...")
    clos = nx.closeness_centrality(g_giant)
    
    print("\nAll calculations completed! Saving in progress...")
    
    # Si salva tutto in un file CSV
    dest_fold = r"c:\Users\douni\Documents\Unipi\Tesi Moltbook\Risultati\Snapshot_23_Aprile.csv"
    os.makedirs(dest_fold, exist_ok=True)
    
    file_name = "Snapshot_23_Aprile.csv"
    rm_path = os.path.join(dest_fold, file_name)
    
    pd.DataFrame({
        'agent_id': list(g_giant.nodes()),
        'in_degree': list(in_deg.values()),
        'pagerank': list(pr.values()),
        'closeness': list(clos.values()),
        'betweenness': list(betw.values())
    }).to_csv(rm_path, index=False, sep=';', decimal=',')
    
    print(f"Analysis successfully completed! File successfully saved in: {rm_path}")
else:
    print("Error: The graph is empty for the specified date")