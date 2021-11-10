import pandas as pd 
import networkx as nx
import argparse

parser = argparse.ArgumentParser(description='Takes a graph as an edgelist (type::head relation type::tail) and stores it as gpickle')

parser.add_argument('--input', "-i", type=str,
                    help='path to the graph stored as edgelist')
parser.add_argument('--output', "-o", type=str,
                    help='path to store the gpickled graph')
parser.add_argument('--sep', "-s", type=str, default = "::",
                    help='seperator between node id and node label/type')


args = parser.parse_args()



df = pd.read_csv(args.input,names=["head","label","tail"],sep="\t") 

G = nx.from_pandas_edgelist(df,create_using=nx.MultiDiGraph(),source="head",target ="tail",edge_attr=True)



node_types = {node: node.split(args.sep)[0] for node in G.nodes}
print(nx.info(G))
nx.set_node_attributes(G, node_types, name='label')


nx.write_gpickle(G, args.output, protocol =4)
