import pandas as pd 
import networkx as nx
import argparse

parser = argparse.ArgumentParser(description='Takes a graph as a gpickle file and stores it as an edgelist.' \
                                             '!!!CAUTION: if the gpickle file contains an undirected graph, this might switch head and tail entities! ')

parser.add_argument('--input', "-i", type=str,
                    help='path to the graph stored as edgelist')
parser.add_argument('--output', "-o", type=str,
                    help='path to store the gpickled graph')
parser.add_argument('--sep', "-s", type=str, default = "::",
                    help='seperator between node id and node label/type')

args = parser.parse_args()

graph = nx.read_gpickle(args.input)


print(nx.info(graph))

with open(args.output, "w") as file:
    for n1, n2, e in graph.edges(data=True):
        file.writelines("{}\t{}\t{}\n".format(n1,e['label'],n2))
        """
        tail_type = e['label'].split(":")[-1]
        if tail_type in n2:
            file.writelines("{}\t{}\t{}\n".format(n1,e['label'],n2))
        elif tail_type in n1:
            file.writelines("{}\t{}\t{}\n".format(n2,e['label'],n1))
        else:
            starting_letter = e['label'][0]
            if n1.startswith(starting_letter):
                file.writelines("{}\t{}\t{}\n".format(n1,e['label'],n2))
            elif n2.startswith(starting_letter):
                file.writelines("{}\t{}\t{}\n".format(n2,e['label'],n1))
            else:
                print("Could not ascertain correct orientation of head and tail entitiy for relation {} in the edge {} {} {}".format(tail_type, n1,e['label'],n2) )
        """