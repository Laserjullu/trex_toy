import networkx as nx

#creates two graphs, with a very different TREX compression ratio but the same density 


G_A = nx.DiGraph()
G_A.add_nodes_from(range(1000))

for i in range(1000):
    G_A.add_edge(i, (i+1)%1000)

# just to match density
G_A.add_edge(100,200)
targets = [0, 1] 
for target in targets:
    for source in range(1000):
        if source != target and not G_A.has_edge(source, target):
            G_A.add_edge(source, target)


G_B = nx.DiGraph()
G_B.add_nodes_from(range(1000))
targets = [0, 1, 2] 
for target in targets:
    for source in range(1000):
        if source != target and not G_B.has_edge(source, target):
            G_B.add_edge(source, target)







nx.write_edgelist(G_A, "graph_A.txt", data = False)
nx.write_edgelist(G_B, "graph_B.txt", data = False)
