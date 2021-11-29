import pandas as pd
import argparse

seed = 1

parser = argparse.ArgumentParser(description='Deletes edges involving compounds and diseases that have been disconnected during filtering from the valdiation and test set.\n' +
                                              '!!!IMPORTANT: This script assumes that your disease node identifier start with "Dsease" and you compounds with "Compound"!')

parser.add_argument('--input', "-i", type=str,
                    help='path to the edgelist of the modified graph')
parser.add_argument('--test', "-t", type=str,
                    help='path to the test set edges')
parser.add_argument('--valid', "-v", type=str,
                    help='path to the validation set edges')

args = parser.parse_args()


modified_edges = pd.read_csv(args.input,sep="\t",names=["head","relation","tail"])

modified_entities = list(set(modified_edges["head"].tolist() + modified_edges["tail"].tolist()))

diseases = [node for node in modified_entities if node.startswith("Disease")]
compounds = [node for node in modified_entities if node.startswith("Compound")]

valid_edges = pd.read_csv(args.valid,sep="\t",names=["compound","relation","disease"])
test_edges = pd.read_csv(args.test,sep="\t",names=["compound","relation","disease"])

# If a compound or a disease didnt make it into the subsampled version of the graph, adjacent "treats" edges are deleted from ground truth

to_delete = []
print("Treats edges in the validation set before deleting: {}.".format(len(valid_edges)))
for i, row in valid_edges.iterrows():
    if row["compound"] not in compounds or row["disease"] not in diseases:
        to_delete.append(i)
print("Found {} edges involving compounds/diseases which are not part of the modified graph.".format(len(to_delete)))
valid_edges.drop(index = to_delete, inplace = True)
print("Treats edges in the validation set after deleting: {}.".format(len(valid_edges)))

to_delete = []
print("Treats edges in the test set before deleting: {}.".format(len(test_edges)))
for i, row in test_edges.iterrows():
    if row["compound"] not in compounds or row["disease"] not in diseases:
        to_delete.append(i)
print("Found {} edges involving compounds/diseases which are not part of the modified graph.".format(len(to_delete)))
test_edges.drop(index = to_delete, inplace = True)
print("Treats edges in the test set after deleting: {}.".format(len(test_edges)))

valid_edges.to_csv("valid_cleaned.txt",sep="\t",header =False, index = False)
test_edges.to_csv("test_cleaned.txt",sep="\t",header =False, index = False)