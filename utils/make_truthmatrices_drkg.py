import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.sparse import coo_matrix, save_npz

seed = 1


subset_entities = pd.read_csv("/home/fratajczak/benchmark/data/drkg/working/subset-with-inverse/entity_ids.del", sep="\t", names=["id", "name"],dtype={"id": int, "name": "string"})
#subset_entities = pd.read_csv("/home/fratajczak/benchmark/data/hetionet-yushan/entity_ids.del".format(fold), sep="\t", names=["id", "name"])

disease_encoder = preprocessing.LabelEncoder()
compound_encoder = preprocessing.LabelEncoder()

diseases = [node for node in subset_entities["name"] if node.startswith("Disease")]
compounds = [node for node in subset_entities["name"] if node.startswith("Compound")]

print(len(diseases))
print(len(compounds))

disease_encoder.fit(diseases)
compound_encoder.fit(compounds)

np.save('/home/fratajczak/benchmark/data/drkg/working/truth_drkg/disease_classes.npy', disease_encoder.classes_)
np.save('/home/fratajczak/benchmark/data/drkg/working/truth_drkg/compound_classes.npy', compound_encoder.classes_)


# unpickle this using:
# encoder = LabelEncoder()
# encoder.classes_ = numpy.load('classes.npy',allow_pickle = True)

# extract the training CtD edges from all the training edges

train_edges_subset = pd.read_csv("/home/fratajczak/benchmark/data/drkg/working/train_treats_unambiguous_union_subset.tsv",sep="\t",names=["head","edge","tail"])
#train_edges_subset = pd.read_csv("/home/fratajczak/kge/data/hetionet-yushan/train.txt".format(fold),sep="\t",names=["head","edge","tail"])

print(len(train_edges_subset))


val_edges_subset = pd.read_csv("/home/fratajczak/benchmark/data/drkg/working/val_unambiguous_union_subset.tsv",sep="\t",names=["head","edge","tail"])
test_edges_subset = pd.read_csv("/home/fratajczak/benchmark/data/drkg/working/test_unambiguous_union_subset.tsv",sep="\t",names=["head","edge","tail"])
print(len(val_edges_subset))
print(len(test_edges_subset))
splits = {'train': train_edges_subset, 'val': val_edges_subset, 'test': test_edges_subset}

for split in ['train','val','test']:
    true_compounds = splits[split]["head"]
    true_diseases = splits[split]["tail"]

    row = np.array(compound_encoder.transform(true_compounds),dtype=np.uint32).flatten()

    col = np.array(disease_encoder.transform(true_diseases),dtype=np.uint32).flatten()

    data = np.ones(row.shape[0], dtype=np.uint8)

    adj = coo_matrix((data, (row, col)), shape=(len(compound_encoder.classes_), len(disease_encoder.classes_)))

    print(adj.shape)
    print(np.sum(adj))

    save_npz("/home/fratajczak/benchmark/data/drkg/working/truth_drkg/ground_truth_{}.npz".format(split),adj)

    splits[split].to_csv("/home/fratajczak/benchmark/data/drkg/working/truth_drkg/ground_truth_{}.tsv".format(split),sep="\t", header =False, index = False)