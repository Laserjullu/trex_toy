import pandas as pd
import networkx as nx
from src.structure.Builder import Builder
import sys
import os
import matplotlib.pyplot as plt

# only reads edgelists in format source target
def trex_on_directory(directory: str):

    results_as_dict = []
    builder = Builder()

    for filename in os.listdir(directory):
        # in case of .DS_store or other
        if filename.startswith('.'):
            continue
        path = directory + "/" + filename
        print("\n Evaluating " + filename)
        G = nx.read_edgelist(path, create_using=nx.DiGraph(), comments = '#')
        trex_graph = builder.build(G)

        entropy = trex_graph.entropy()
        results_as_dict.append({"Dataset": filename, "n": G.number_of_nodes(), "m": G.number_of_edges(),
                                "Basic Array Entropy": entropy[0], "Bitvector representation Entropy": entropy[1], "Reduced Entropy": entropy[2], 
                                "density": nx.density(G), "avg cc" : nx.average_clustering(G), "relative savings": 1 - entropy[2]/entropy[1]})
    
    print(results_as_dict)
    return pd.DataFrame(results_as_dict)




df = trex_on_directory(sys.argv[1])
df.plot(kind= "scatter", x = "density", y = "relative savings" )
df.plot(kind= "scatter", x = "avg cc", y = "relative savings" )
plt.show()
