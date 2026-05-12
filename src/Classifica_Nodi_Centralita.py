import pandas as pd

# Si carica il file CSV con i dati dei nodi e le loro misure di centralità
file_path = r"c:\Users\douni\Documents\Unipi\Tesi Moltbook\Risultati\Snapshot_23_Aprile.csv"
print(f"Loading data from: {file_path}")

try:
    df = pd.read_csv(file_path, sep=';', decimal=',')
except FileNotFoundError:
    print("Error: File not found")
    exit()

print("Calculating ranking positions...")

# Si calcolano le posizioni di classifica per ciascuna misura di centralità
df['rank_in_degree'] = df['in_degree'].rank(ascending=False, method='min').astype(int)
df['rank_pagerank'] = df['pagerank'].rank(ascending=False, method='min').astype(int)
df['rank_betweenness'] = df['betweenness'].rank(ascending=False, method='min').astype(int)
df['rank_closeness'] = df['closeness'].rank(ascending=False, method='min').astype(int)

# Si estraggono i Top 100 per ciascuna misura di centralità
top_in = df.nlargest(100, 'in_degree')['agent_id']
top_pr = df.nlargest(100, 'pagerank')['agent_id']
top_bw = df.nlargest(100, 'betweenness')['agent_id']
top_cl = df.nlargest(100, 'closeness')['agent_id']

# Si uniscono tutti i nodi elite in un unico set per evitare duplicati
elite_nodes = set(top_in).union(set(top_pr), set(top_bw), set(top_cl))

print(f"Found {len(elite_nodes)} unique nodes that fall into at least one Top 100 category")

# Si filtra il DataFrame originale per mantenere solo i nodi elite
df_elite = df[df['agent_id'].isin(elite_nodes)].copy()

# Si ordina la tabella finale per PageRank -> se si volesse ordinare per un'altra metrica, basta cambiare 'rank_pagerank' 
df_elite = df_elite.sort_values('rank_pagerank')

# Si riordinano le colonne per una migliore leggibilità
ord_col = [
    'agent_id', 
    'rank_pagerank', 'pagerank', 
    'rank_betweenness', 'betweenness', 
    'rank_in_degree', 'in_degree', 
    'rank_closeness', 'closeness'
]
df_elite = df_elite[ord_col]

# Si salvano i risultati in un nuovo file CSV
output_path = r"C:\Users\douni\Documents\Unipi\Tesi Moltbook\Risultati\Classifica_Top_Nodi.csv"
df_elite.to_csv(output_path, index=False, sep=';', decimal=',')

print(f"\nElite node table successfully saved in: {output_path}")
print("\nPreview of the first 5 Elite Nodes (sorted by PageRank):")
print(df_elite.head(5).to_string(index=False))