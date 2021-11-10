import pandas as pd
from sklearn.model_selection import train_test_split
import argparse

parser = argparse.ArgumentParser(description='Splits the treats edges into train, validation and test.\n' \
                                             'It produces train/test/val.txt which together contain all relations that also appear in the input graph \n' \
                                             'and ground_truth_train/test/val.txt which contain only the treats relations.\n' \
                                             'Example usage: python3 ~/metafilter-apply/utils/split.py -i full.txt -t CtD -s 1 -x 0.25')

parser.add_argument('--input', "-i", type=str,
                    help='path to an edgelist containing all relations')
parser.add_argument('--treats_identifier', "-t", type=str, default="CtD",
                    help='The exact and complete identifier of the treats relation')
parser.add_argument('--seed', "-s", type=int, default=1,
                    help='seed for splitting')
parser.add_argument('--holdout_size', "-x", type=float, default=0.2,
                    help='Total size of holdout set as a fraction of the input edgelist. Test and Validation will each be half of that.')

args = parser.parse_args()

edges = pd.read_csv(args.input,sep="\t",names=["head","relation","tail"])

treats_edges = edges[edges["relation"] == args.treats_identifier]
non_treats_edges = edges[edges["relation"] != args.treats_identifier]

train, val = train_test_split(treats_edges, test_size=0.2, shuffle=True,random_state=args.seed)
val, test = train_test_split(val, test_size=0.5,random_state=args.seed)

splits = {'train': train, 'valid': val, 'test': test}

for split in ['train','valid','test']:
    if split == "train":
        full_train = pd.concat((non_treats_edges, splits[split]))
        full_train.to_csv("{}.txt".format(split),sep="\t", header =False, index = False)
    else:      
        splits[split].to_csv("{}.txt".format(split),sep="\t", header =False, index = False)

    print("{} treats edges in the {} set.".format(len(splits[split]),split))
    splits[split].to_csv("ground_truth_{}.txt".format(split),sep="\t", header =False, index = False)

