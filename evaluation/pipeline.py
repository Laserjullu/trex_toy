import pandas as pd
import networkx as nx
from src.structure.Builder import Builder
from evaluation.evaluator import Evaluator
import os
import time
import argparse
import numpy as np

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
            trex_time = time.time() - start

            start = time.time()
            metrics = Evaluator.evaluate(G, G_minus_T, G_built, G_greedy, planar=True)
            evaluation_time = time.time() - start
            metrics["Dataset"] = filename
            metrics["trex vs bitvector (greedy) (%)"] = (1 - metrics["total bits trex"] / metrics["bitvector greedy total bits"]) * 100
            metrics["trex time"] = trex_time
            metrics["evaluation time"] = evaluation_time
            results_as_dict.append(metrics)
        else:
            G = nx.read_edgelist(path, create_using=nx.DiGraph(), comments = '#')
            start = time.time()
            G_built, G_minus_T = builder.build(G)
            trex_time = time.time() - start

            start = time.time()
            metrics = Evaluator.evaluate(G, G_minus_T, G_built, planar=True)
            evaluation_time = time.time() - start
            metrics["Dataset"] = filename
            metrics["trex vs bitvector (greedy) (%)"] = (1 - metrics["total bits trex"] / metrics["bitvector total bits"]) * 100
            metrics["trex time"] = trex_time
            metrics["evaluation time"] = evaluation_time
            results_as_dict.append(metrics)
        print(metrics)
        
    df = pd.DataFrame(results_as_dict)
    # some more derived metrics:
    df["trex vs array (%)"] = (1 - df["total bits trex"] / df["array total bits"]) * 100
    df["planar vs trex (%)"] = (1 - df["total bits planar"] / df["total bits trex"]) * 100
    df["trex bpe"] = df["total bits trex"] / df["m"]
    df["planar bpe"] = df["total bits planar"] / df["m"]
    df["planar edges vs maximum"] = 100 * df["planar edges"]/(np.floor(df["n"] * 1.5 - 1.5))

    df["DUB vs trex"] = df["DUB"] - df["trex entropy"]
    df["normalized DUB difference"] = df["DUB vs trex"] / (df["n"] * np.log2(df["n"]))

    df["NIB vs trex"] = df["NIB"] - df["trex entropy"]
    df["normalized NIB difference"] = df["NIB vs trex"] / (df["n"] * np.log2(df["n"]))

    df["alpha 1.7"] = df["n"]/df["non zero indegree nodes"]
    df["density"] = df["m"]/df["n"]
    df.to_csv(output_path, sep = ';', decimal = ',')
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--undirected", action = "store_true")
    parser.add_argument("--output")

    args = parser.parse_args()
    if args.undirected:
        if args.output:
            df = trex_on_directory(args.directory, undirected = True, output_path = args.output)
        else: 
            df = trex_on_directory(args.directory, undirected = True)
    else:
        if args.output:
            df = trex_on_directory(args.directory, undirected = False, output_path = args.output)
        else: 
            df = trex_on_directory(args.directory, undirected = False)

