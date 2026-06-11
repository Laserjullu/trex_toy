import pandas as pd
import networkx as nx
from src.structure.Builder import Builder
import sys
import os
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
import argparse
# only reads edgelists in format source target
def trex_on_directory(directory: str, output_path = "trex_results.csv", undirected = False):

    results_as_dict = []
    builder = Builder()

    for filename in os.listdir(directory):
        # in case of .DS_store or other
        if filename.startswith('.'):
            continue
        path = directory + "/" + filename
        print("\n Evaluating " + filename)
        if undirected:
            G = nx.read_edgelist(path, create_using=nx.Graph(), comments = '#')
        else:
            G = nx.read_edgelist(path, create_using=nx.DiGraph(), comments = '#')

        start = time.time()
        # not yet planar extraction for undirected graphs
        if undirected:
            trex_graph = builder.build(G, planar = True)
        else:
            trex_graph = builder.build(G, planar = True)
        end = time.time()
        print("Time taken for Trex Building: " + str(end - start))
        entropy = trex_graph.entropy_tuple
        if undirected: 
            results_as_dict.append({"Dataset": filename, "n": G.number_of_nodes(), "m": G.number_of_edges(),
                                "Basic Array Entropy": entropy[0], "Bitvector representation Entropy": entropy[1], 
                                "Bitvector representation with random choices": entropy[2], "Bitvector representation with greedy choices": entropy[3], 
                                "Reduced Entropy": entropy[4], "Planar extraction entropy": entropy[5],
                                "avg cc" : nx.average_clustering(G), "alpha 1.6": trex_graph.alpha_16, "non zero indegree": trex_graph.non_zero_indegrees,
                                 "upper bound 1.6": trex_graph.upper_bound_16, "upper bound 1.7": trex_graph.upper_bound_17, "indegree variance": trex_graph.indegree_variance,
                                 "number of classes": trex_graph.num_classes})
        else:
            results_as_dict.append({"Dataset": filename, "n": G.number_of_nodes(), "m": G.number_of_edges(),
                                "Basic Array Entropy": entropy[0], "Bitvector representation Entropy": entropy[1], 
                                "Reduced Entropy": entropy[2], "Planar extraction entropy": entropy[3], 
                                "avg cc" : nx.average_clustering(G), "alpha 1.6": trex_graph.alpha_16, "non zero indegree": trex_graph.non_zero_indegrees,
                                 "upper bound 1.6": trex_graph.upper_bound_16, "upper bound 1.7": trex_graph.upper_bound_17, "indegree variance": trex_graph.indegree_variance,
                                 "number of classes": trex_graph.num_classes})
    df = pd.DataFrame(results_as_dict)
    df.to_csv(output_path)
    print(results_as_dict)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--undirected", action = "store_true")

    args = parser.parse_args()
    if args.undirected:
        df = trex_on_directory(args.directory, undirected = True)
    else:
        df = trex_on_directory(args.directory, undirected = False)

    if args.undirected:
        plot = df.plot.bar(x = "Dataset", y = ["Basic Array Entropy", "Bitvector representation Entropy", "Bitvector representation with random choices", "Bitvector representation with greedy choices", "Reduced Entropy", "Planar extraction entropy"])
    else:
        plot = df.plot.bar(x = "Dataset", y = ["Basic Array Entropy", "Bitvector representation Entropy", "Reduced Entropy", "Planar extraction entropy"])
    plt.show()
