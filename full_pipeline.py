import os
import sys 
import argparse
import logging
import datetime
from metapathWalking import getConfiguredLogger


parser = argparse.ArgumentParser(description='Does a complete graph modification given an input graph and a list of metapaths.')

parser.add_argument('--input', "-i", type=str,
                    help='path to the input graph (training edges only). Accepts tsv (edglist, triplestore), gpickle (networkx) or graphml.')
parser.add_argument('--input_sep', "-c", type=str, default = "::",
                    help='seperator between node id and node label/type in case the input is passed as a tsv edglist.')
parser.add_argument('--input_split_size', "-x", type=float, default = 0,
                    help='Size of holdout set. Test and val will each be half of that size. If 0 is passed, no split is performed. If you did not prepare you train/val/test splits, ' +
                         'beforehand and wish to do it within this script, pass the input graph as a tsv edgelist to avoid edge direction ambiguity in undirected gpickle formats.')
parser.add_argument('--input_split_relation', "-r", type=str, default = "treats",
                    help='Relation that should be split into train/val/test sets.')
parser.add_argument('--input_split_seed', "-d", type=int, default = 1,
                    help='Relation that should be split into train/val/test sets.')

parser.add_argument('--output', "-o", type=str,
                    help='path to store the final modified graph')

parser.add_argument('--walking_metapaths', "-p", type=str, default="default",
                    help='metapaths consisting of comma seperated node types, one metapath per line.')
parser.add_argument('--walking_njobs', "-n", type=int, default=4,
                    help='number of concurrent workers for walking')
parser.add_argument('--walking_nwalks', "-w", type=int, default=5000,
                    help='number of collected concatenated walks per metapath')
parser.add_argument('--walking_nstarts', "-s", type=int, default=1000,
                    help='number of starts per node of first node type for each metapath')
parser.add_argument('--walking_length', "-l", type=int, default=100,
                    help='desired length of concatenated metapaths')


args = parser.parse_args()

def main():

    logger = getConfiguredLogger("Pipeline")

    logger.info("Starting Graph Modification Pipeline at {}".format(datetime.datetime.now()))

    if args.input_split_size > 0.000001:

        logger.info("input.split_size greater than 0, performing train/test/val split.")
        failure = os.system("python3 utils/split.py --input {} --treats_identifier {} --seed {}".format(args.input, args.input_split_relation, args.input_split_seed))
        if failure:
            exit(1)
        args.input = "train.txt"

    if args.input[-7:] not in ["gpickle", "graphml"]:
        logger.info("Input not in gpickle or graphml format, gpickling it.")
        input_base =  ".".join(args.input.split(".")[:-1])  
        failure = os.system("python3 utils/pickle_graph.py --input {} --sep {} --output {}".format(args.input, args.input_sep, input_base + ".gpickle"))
        if failure:
            exit(1)
        args.input = input_base + ".gpickle"
        


    logger.info("Walking graph with {} parallel workers.".format(args.walking_njobs))
    failure = os.system("python3 metapathWalking.py --input {} --output {} --metapaths {} --njobs {} --nwalks {} --nstarts {} --length {}".format(
                                                     args.input, "walks.txt" , args.walking_metapaths, args.walking_njobs, args.walking_nwalks, args.walking_nstarts, args.walking_length))
    if failure:
            exit(1)

    logger.info("Walking is done, uniquifying node ids.")
    failure = os.system("python3 process_walks.py --input walks.txt --output unique_ids.txt".format(args.walking_njobs))
    if failure:
            exit(1)

    logger.info("Unique node ids obtained, modifying original graph.")
    failure = os.system("python3 subset_graph.py --list unique_ids.txt --graph {} --output {}".format(args.input, args.output))
    if failure:
            exit(1)

    logger.info("Modification of original graph is complete. Please make sure that none of the deleted nodes is incident to an edge from you test and val sets." +
                " See utils/delete_disconnected.py on how to do this.")


if __name__ == "__main__":
    main()

