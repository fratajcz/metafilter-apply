import networkx as nx
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Keeps a list of nodes from a graph, deletes the rest.')

parser.add_argument('--list', "-l", type=str,
                    help='path to the list of nodes that should be kept in the graph')
parser.add_argument('--graph', "-g", type=str,
                    help='path to the graph that has to be filtered.')
parser.add_argument('--output', "-o", type=str,
                    help='path to store the modified graph')


args = parser.parse_args()



unique_nodes = args.list

path=args.graph


if path[-6:] == "pickle":
    graph = nx.read_gpickle(path)
elif path[-7:] == "graphml":
    graph = nx.read_graphml(path)
else:
    df = pd.read_csv(path,names=["head","label","tail"],sep="\t")
    graph = nx.from_pandas_edgelist(df,create_using=nx.MultiDiGraph(),source="head",target ="tail",edge_attr=True)

nodes_to_keep = []

with open(unique_nodes,"r") as file:
    for line in file:
        nodes_to_keep.append(line.strip())   





print(nx.info(graph))
all_nodes = graph.nodes()

nodes_to_delete = set(all_nodes) - set(nodes_to_keep)
graph.remove_nodes_from(nodes_to_delete)
print(nx.info(graph))

if "hetionet" in path:
    # for hetionet:
    label = nx.get_node_attributes(graph, 'label')
    identifier = nx.get_node_attributes(graph, 'identifier')
    with open(args.output, "w") as file:
        for n1, n2, e in graph.edges(data=True):
            file.writelines("{}::{}\t{}\t{}::{}\n".format(label[n1][1:],identifier[n1],e['label'],label[n2][1:],identifier[n2]))
else:
    # for DRKG:
    with open(args.output, "w") as file:
        for n1, n2, e in graph.edges(data=True):
                file.writelines("{}\t{}\t{}\n".format(n1,e['label'],n2))
