import networkx as nx
from tqdm import tqdm


# Implementation of Greedy++ from "Flowless: Extracting Densest Subgraphs Without Flow Computations" with added support for multigraphs, using the exact same density definition.
# For iterations == 1 exactly on par with Charikars Greedy.

# Slight modification of NetworkX's implementation for undirected Graphs

def density_greedy(G, iterations):
    if G.number_of_edges() == 0:
        return 0.0, set()
    if iterations < 1:
        raise ValueError(
            f"The number of iterations must be an integer >= 1. Provided: {iterations}"
        )

    loads = {node: 0 for node in G.nodes}  # Load vector for Greedy++.
    best_density = 0.0  # Highest density encountered.
    best_subgraph = set()  # Nodes of the best subgraph found.

    for _ in tqdm(range(iterations)):
        # Initialize heap for fast access to minimum weighted degree.
        heap = nx.utils.BinaryHeap()

        # Compute initial weighted degrees and add nodes to the heap.
        for node, degree in G.degree:
            heap.insert(node, loads[node] + degree)
        # Set up tracking for current graph state.
        remaining_nodes = set(G.nodes)
        num_edges = G.number_of_edges()
        current_degrees = dict(G.degree)

        while remaining_nodes:
            num_nodes = len(remaining_nodes)

            # Current density of the (implicit) graph
            current_density = num_edges / num_nodes

            # Update the best density.
            if current_density > best_density:
                best_density = current_density
                best_subgraph = set(remaining_nodes)

            # Pop the node with the smallest weighted degree.
            node, _ = heap.pop()
            if node not in remaining_nodes:
                continue  # Skip nodes already removed.

            # Update the load of the popped node.
            loads[node] += current_degrees[node]

            # Update neighbors' degrees and the heap.
            for neighbor in G.neighbors(node):
                if neighbor in remaining_nodes:
                    # first determine the number of parallel edges and then subtract accordingly, implicitly works on regular Graphs as well. Rest of the method alrady properly works on multigraphs too. 
                    if 'weight' in G[node][neighbor]:
                        multiplicity = G[node][neighbor]['weight']
                    else:
                        multiplicity = 1
                    current_degrees[neighbor] -= multiplicity
                    num_edges -= multiplicity
                    heap.insert(neighbor, loads[neighbor] + current_degrees[neighbor])

            # Remove the node from the remaining nodes.
            remaining_nodes.remove(node)

    return best_density, best_subgraph

