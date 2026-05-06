import matplotlib.pyplot as plt
from collections import Counter

from Analisi import G

print("\nCalculating degree distributions...")

# Si estraggono i gradi
in_degrees = [degree for node, degree in G.in_degree() if degree > 0]
out_degrees = [degree for node, degree in G.out_degree() if degree > 0]

# Si contano quante persone hanno un certo grado (sia in che out)
in_counts = Counter(in_degrees)
out_counts = Counter(out_degrees)

# Si separano le coordinate X (il grado) e Y (quante persone hanno quel grado)
in_x, in_y = zip(*in_counts.items())
out_x, out_y = zip(*out_counts.items())

# Grafico 1: In-Degree (Popolarità)
plt.figure(figsize=(10, 7)) # Inizializza la prima finestra
plt.scatter(in_x, in_y, color='royalblue', alpha=0.6, s=30, label='In-Degree')
plt.xscale('log')
plt.yscale('log')
plt.title("Distribuzione Power-Law: In-Degree\n(Popolarità passiva - ricevono commenti)", fontsize=18, fontweight='bold')
plt.xlabel("Grado - Numero di Interazioni", fontsize=14)
plt.ylabel("Numero di Utenti", fontsize=14)
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend(fontsize=12, loc='upper right')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

# Grafico 2: Out-Degree (Attività)
plt.figure(figsize=(10, 7)) # Inizializza la seconda finestra
plt.scatter(out_x, out_y, color='crimson', alpha=0.6, s=30, label='Out-Degree', marker='x')
plt.xscale('log')
plt.yscale('log')
plt.title("Distribuzione Power-Law: Out-Degree\n(Attività esplicita - scrivono commenti)", fontsize=18, fontweight='bold')
plt.xlabel("Grado - Numero di Interazioni", fontsize=14)
plt.ylabel("Numero di Utenti", fontsize=14)
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend(fontsize=12, loc='upper right')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

# Mostra entrambe le finestre generate contemporaneamente
plt.show()