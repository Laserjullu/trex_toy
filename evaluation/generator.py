import networkx as nx

class GraphGenerator:

    @staticmethod 
    def generate_graphs():
        G_erdos_renyi = nx.erdos_renyi_graph(20000, 0.005)
        nx.write_edgelist(G_erdos_renyi, "G_erdos_renyi.txt")

        G_bipartite = nx.complete_bipartite_graph(1000, 1000)
        nx.write_edgelist(G_bipartite, "G_bipartite.txt")

        G_barabasi_albert = nx.barabasi_albert_graph(40000, 14)
        nx.write_edgelist(G_barabasi_albert, "G_barabasi_albert.txt")

if __name__ == "__main__":
    GraphGenerator.generate_graphs()


