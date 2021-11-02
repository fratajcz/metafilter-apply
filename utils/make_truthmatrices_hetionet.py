import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.sparse import coo_matrix, save_npz

seed = 1

base_path = "./kge/"

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1','True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0','False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f","--fromdataset",type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Do not calculate splits but instead use train/val/test splits from libkge dataset")
parser.add_argument("-p","--path",type=str, default="", help="path to the directory where libkge dataset is stored.")
args = parser.parse_args()
"""

for fold in [2,3,4]:
    #subset_entities = pd.read_csv("/home/fratajczak/benchmark/data/hetionet/inspection/entities_fold{}_subset".format(fold), sep="\t", names=["name"])
    subset_entities = pd.read_csv(base_path + "data/hetionet-fold{}-subset-with-inverse/entity_ids.del".format(fold), sep="\t", names=["id", "name"])

    disease_encoder = preprocessing.LabelEncoder()
    compound_encoder = preprocessing.LabelEncoder()

    diseases = [node for node in subset_entities["name"] if node.startswith("Disease")]
    compounds = [node for node in subset_entities["name"] if node.startswith("Compound")]

    print(len(diseases))
    print(len(compounds))

    disease_encoder.fit(diseases)
    compound_encoder.fit(compounds)

    np.save(base_path + 'truth_hetionet/disease_classes_fold{}.npy'.format(fold), disease_encoder.classes_)
    np.save(base_path + 'truth_hetionet/compound_classes_fold{}.npy'.format(fold), compound_encoder.classes_)

    # unpickle this using:
    # encoder = LabelEncoder()
    # encoder.classes_ = numpy.load('classes.npy',allow_pickle = True)

    # extract the training CtD edges from all the training edges

    train_edges_subset = pd.read_csv(base_path + "data/hetionet-fold{}-subset-with-inverse/train.txt".format(fold),sep="\t",names=["head","edge","tail"])
    #train_edges_subset = pd.read_csv("/home/fratajczak/kge/data/hetionet-yushan/train.txt".format(fold),sep="\t",names=["head","edge","tail"])
    train_edges_subset = train_edges_subset[train_edges_subset["edge"] == "CtD"]
    print(len(train_edges_subset))


    val_edges_subset = pd.read_csv(base_path + "data/hetionet-fold{}-subset-with-inverse/valid.txt".format(fold),sep="\t",names=["head","edge","tail"])
    val_edges_subset = val_edges_subset[val_edges_subset["edge"] == "CtD"]
    test_edges_subset = pd.read_csv(base_path + "data/hetionet-fold{}-subset-with-inverse/test.txt".format(fold),sep="\t",names=["head","edge","tail"])
    test_edges_subset = test_edges_subset[test_edges_subset["edge"] == "CtD"]
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

        save_npz(base_path + "truth_hetionet/ground_truth_{}_fold{}.npz".format(split, fold),adj)

        splits[split].to_csv(base_path + "truth_hetionet/ground_truth_{}_fold{}.tsv".format(split,fold),sep="\t", header =False, index = False)