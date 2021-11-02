import pandas as pd 
import networkx as nx

path = "/home/fratajczak/benchmark/data/drkg/train.gpickle.test"


graph = nx.read_gpickle(path)


print(nx.info(graph))

with open(path.split(".")[0] + ".tsv", "w") as file:
    for n1, n2, e in graph.edges(data=True):
        tail_type = e['label'].split(":")[-1]
        if tail_type in n2:
            file.writelines("{}\t{}\t{}\n".format(n1,e['label'],n2))
        elif tail_type in n1:
            file.writelines("{}\t{}\t{}\n".format(n2,e['label'],n1))
        else:
            print("Could not find tail type {} in the edge {} {} {}".format(tail_type, n1,e['label'],n2) )
