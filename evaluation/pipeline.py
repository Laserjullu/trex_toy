import pandas as pd
import networkx as nx
from src.structure.Builder import Builder
from evaluation.evaluator import Evaluator
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
            start = time.time()
            G_built, G_minus_T, G_greedy = builder.build(G)
            print("Time taken for Trex Building: " + str(time.time() - start))

            start = time.time()
            metrics = Evaluator.evaluate(G, G_minus_T, G_built, G_greedy, planar=True)
            print("Time taken for Evaluation: " + str(time.time() - start))
            metrics["Dataset"] = filename
            results_as_dict.append(metrics)
            print(metrics)
        else:
            G = nx.read_edgelist(path, create_using=nx.DiGraph(), comments = '#')
            start = time.time()
            G_built, G_minus_T = builder.build(G)
            print("Time taken for Trex Building: " + str(time.time() - start))

            start = time.time()
            metrics = Evaluator.evaluate(G, G_minus_T, G_built, planar=True)
            print("Time taken for Evaluation: " + str(time.time() - start))
            metrics["Dataset"] = filename
            results_as_dict.append(metrics)
            print(metrics)

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
        plot = df.plot.bar(x = "Dataset", y = ["array entropy", "bitvector entropy", "bitvector random entropy", "bitvector greedy entropy", "reduced entropy", "planar entropy"])
    else:
        plot = df.plot.bar(x = "Dataset", y = ["array entropy", "bitvector entropy", "reduced entropy", "planar entropy"])
    plt.show()
