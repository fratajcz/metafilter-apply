import matplotlib.pyplot as plt
import os
import networkx as nx
import numpy as np
import stellargraph as sg
from stellargraph import StellarGraph
from stellargraph.data import UniformRandomMetaPathWalk
import datetime
from joblib import Parallel, delayed
import math
import argparse
import random
import pandas as pd

parser = argparse.ArgumentParser(description='Walk a Graph along Metapaths and store complete walks.')

parser.add_argument('--input', "-i", type=str,
                    help='path to a graphml or gpickle file of hetionet or drkg')
parser.add_argument('--output', "-o", type=str,
                    help='path to store the walks')
parser.add_argument('--metapaths', "-p", type=str, default="",
                    help='metapaths consisting of comma seperated node types, one metapath per line.')
parser.add_argument('--njobs', "-n", type=int, default=4,
                    help='number of concurrent workers for walking')
parser.add_argument('--nwalks', "-w", type=int, default=5000,
                    help='number of collected concatenated walks per metapath')
parser.add_argument('--nstarts', "-s", type=int, default=1000,
                    help='number of starts per node of first node type for each metapath')


args = parser.parse_args()

def getConfiguredLogger(name):
    from yaml import load, Loader
    import logging
    import logging.config

    with open("logger.yaml", "r") as file:
        config = load(file, Loader=Loader)

    logging.config.dictConfig(config)

    return logging.getLogger(name)

def loadGraphData(path):
    logger = getConfiguredLogger(__name__)
    dataset_location = os.path.expanduser(path)
    if path[-6:] == "pickle":
        g_nx = nx.read_gpickle(dataset_location)
    elif path[-7:] == "graphml":
        g_nx = nx.read_graphml(dataset_location)

    logger.debug("Number of nodes {} and number of edges {} in graph.".format(g_nx.number_of_nodes(), g_nx.number_of_edges()))

    # sg has a problem with the edge attribute "source", which is confused with the "source" in source node / target node of an edge
    for n1, n2, d in g_nx.edges(data=True):
     if "source" in d.keys():
        del d["source"]

    stellar_g_nx = StellarGraph.from_networkx(g_nx.to_undirected())
    logger.debug("Number of nodes {} and number of edges {} in graph.".format(stellar_g_nx.number_of_nodes(), stellar_g_nx.number_of_edges()))
    logger.debug("Node types in the graph: {}".format(stellar_g_nx.node_types))

    del g_nx

    return stellar_g_nx


A = 'Anatomy'
BP = 'BiologicalProcess'
CC = 'CellularComponent'
C = 'Compound'
D = 'Disease'
G = 'Gene'
MF = 'MolecularFunction'
PC = 'PharmacologicClass'
SE = 'SideEffect'
S = 'Symptom'
PW = 'Pathway'

asymmetric_metapaths = [
[C,C,C,C,D],
[C,C,C,D],
[C,C,C,G,D],
[C,C,D],
[C,C,D,C,D],
[C,C,G,A,D],
[C,C,G,C,D],
[C,C,G,D],
[C,C,G,D,D],
[C,C,G,G,D],
[C,C,PC,C,D],
[C,D,C,D],
[C,D,C,D,D],
[C,D,D],
[C,D,D,A,D],
[C,D,D,S,D],
[C,G,A,D],
[C,G,A,D,D],
[C,G,A,G,D],
[C,G,BP,G,D],
[C,G,C,C,D],
[C,G,C,D],
[C,G,C,D,D],
[C,G,C,G,D],
[C,G,D],
[C,G,D,A,D],
[C,G,D,D],
[C,G,D,D,D],
[C,G,D,G,D],
[C,G,D,S,D],
[C,G,G,A,D],
[C,G,G,C,D],
[C,G,G,D],
[C,G,G,D,D],
[C,G,G,G,D],
[C,G,MF,G,D],
[C,G,PW,G,D],
[C,PC,C,C,D],
[C,PC,C,D],
[C,PC,C,G,D],
[C,SE,C,D],
[C,SE,C,D,D],
[C,SE,C,G,D],
]

circular_metapaths = [x + [C] for x in asymmetric_metapaths]

def doTheWalk(metapath, num_starts = 1000):
    logger = getConfiguredLogger(__name__)
    logger.debug('Initializing Walker...')
    global path
    graph = loadGraphData(path = path)
    rw = UniformRandomMetaPathWalk(graph)
    logger.debug('Walker initialized.')

    starttime = datetime.datetime.now().time()

    logger.debug('start: ' + str(starttime))

    forward_metapath= metapath + [metapath[0]]  # eg. make ['C','C','D'] to ['C','C','D','C']
    backward_metapath = metapath[::-1] + [metapath[-1]] # eg. make ['C','C','D'] to ['D','C','C','D']

    walks_forward = rw.run(nodes=list(graph.nodes()),
            n=num_starts,
            length=len(forward_metapath),
            metapaths=[forward_metapath])

    logger.debug('forward walks done: ' + str(datetime.datetime.now().time()))

    walks_backward = rw.run(nodes=list(graph.nodes()),
            n=num_starts,
            length=len(backward_metapath),
            metapaths=[backward_metapath])


    logger.debug('finished: ' + str(datetime.datetime.now().time()))

    logger.debug("Number of random walks for metapath {}: {} forwards and: {} backwards".format(str(metapath),len(walks_forward),len(walks_backward)))
    del graph
    del rw
    return walks_forward,walks_backward

def trimWalklets(walks_forward,walks_backward,metapath):
    logger = getConfiguredLogger(__name__)
    logger.debug(metapath)
    minimum_length = len(metapath)
    logger.debug('desired length: {}'.format(minimum_length))

    good_walks_forward =  [x[0:minimum_length] for x in walks_forward if len(x)>=minimum_length]

    good_walks_backward =  [x[0:minimum_length] for x in walks_backward if len(x)>=minimum_length]
    logger.debug('length metrics before trimming:')
    logger.debug(np.quantile([len(x) for x in walks_forward],[0,0.05,0.10,0.25,0.5,0.75,0.90,0.95,1]))
    logger.debug(np.quantile([len(x) for x in walks_backward],[0,0.05,0.10,0.25,0.5,0.75,0.90,0.95,1]))
    logger.debug('length metrics after trimming:')
    logger.debug(np.quantile([len(x) for x in good_walks_forward],[0,0.05,0.10,0.25,0.5,0.75,0.90,0.95,1]))
    logger.debug(np.quantile([len(x) for x in good_walks_backward],[0,0.05,0.10,0.25,0.5,0.75,0.90,0.95,1]))
    logger.debug('example for forward walks: {}'.format(good_walks_forward[0]))
    logger.debug('example for backward walks: {}'.format(good_walks_backward[0]))
    return good_walks_forward,good_walks_backward



def constructDicts(good_walks_forward,good_walks_backward):
    backwalk_dict = {}

    for backwalk in good_walks_backward:
        if  not backwalk[0] in backwalk_dict:
            backwalk_dict[backwalk[0]] = (tuple([backwalk]))
        else:
            backwalk_dict[backwalk[0]] = backwalk_dict[backwalk[0]] + (backwalk,)

    forwardwalk_dict = {}

    for forwardwalk in good_walks_forward:
        if  not forwardwalk[0] in forwardwalk_dict:
            forwardwalk_dict[forwardwalk[0]] = (tuple([forwardwalk]))
        else:
            forwardwalk_dict[forwardwalk[0]] = forwardwalk_dict[forwardwalk[0]] + (forwardwalk,)

    logger.debug(len(forwardwalk_dict))
    logger.debug(len(backwalk_dict))

    return forwardwalk_dict,backwalk_dict

def recursiveConcat(forwardDict,backwardDict,walk,length):
    ''' Function extends the short walklets to walks of at least the desired length

    Parameters
        ----------
        forwardDict : dictionary
            Contains the dictionary of the forward-walklets on the chosen metapath.
            The Keys are the first nodes of the walklets and the Values are tuples of lists of the walklets.
            Example: {'n0': (['n0','n1','n2'],['n0','n3','n4'],[...])'}

        backwardDict : dictionary
            Same as forwardDict, but the walklets for the walk back on the metapath.

        walk : [str]
            Contains the already concatenated walk.
            Must be initalized when calling the function, e.g. by passing one random backward-walklet by passing
            walk = random.choice(list(backwardDict.values()))[0]

        length : int
            The desired length of the walk.
            Note that the walk can get longer if the walk length ist not an exact multiple of the walklet length.

    Returns
        ----------
        walk : [str]


    '''

    if len(walk) >= length:                                              # finishing criterion
        return walk
    else:
        if walk[-1] in forwardDict:                            # check if forwardwalk extends current walk
            [walk.append(x) for x in random.choice(forwardDict[walk[-1]])[1:]] # if so, append it to the walk and continue searching
            if walk[-1] in backwardDict:                   # check if backwardwalk extends current walk
                [walk.append(x) for x in random.choice(backwardDict[walk[-1]])[1:]]    # if so, apend it to the walk
                return recursiveConcat(forwardDict,backwardDict,walk,length)  # do it all again

def buildWalks(forwardDict,backwardDict,length,numWalks):
    walks= []

    while len(walks) < numWalks:
        walk = recursiveConcat(forwardDict,backwardDict, walk=random.choice(list(backwardDict.values()))[0],length=length)
        if walk is not None:
            walks.append(walk)

    return walks


def getWalksForThisMetapath(metapath,numWalks):

    walks_forward,walks_backward = doTheWalk(metapath, args.nstarts)

    good_walks_forward,good_walks_backward = trimWalklets(walks_forward,walks_backward,metapath)

    forwardwalk_dict,backwalk_dict = constructDicts(good_walks_forward,good_walks_backward)

    walks = buildWalks(forwardwalk_dict,backwalk_dict,100,numWalks) # [[walk],[walk]]

    writeWalks_byline(walks,path=args.output)

    del good_walks_forward, good_walks_backward

    #return walks

def getWalks(metapaths,numWalks=5000):
    metawalks= []

    for metapath in metapaths:
        [metawalks.append(x) for x in getWalksForThisMetapath(metapath,numWalks)]

    return metawalks

def getWalksParallel(metapaths,numWalks=5000):

    jobs= args.njobs

    logger.debug('Walking {} Metapaths in {} Processes.'.format(len(metapaths),jobs))

    Parallel(n_jobs=jobs,verbose=10)(delayed(getWalksForThisMetapath)(i,numWalks) for i in metapaths)


def writeWalks(walks):
    with open('walks_out.txt', 'a') as the_file:
        the_file.write(str(walks))


def writeWalks_byline(walks,path):
    '''Writes the walks to the path, nodes being whitespace seperated und one walk per line'''

    with open(path, 'a') as the_file:
        for walk in walks:
            the_file.write(" ".join(walk) + "\n")
            

if __name__ == '__main__':
    # Initalize global variables
    logger = getConfiguredLogger(__name__)

    path = args.input

    

    if args.metapaths == "default":

        metapaths = asymmetric_metapaths

        if "drkg" in path:

            AT = 'Atc'
            additional_metapaths = [[C,AT,C,D],
            [C,AT,C,D,D],
            [C,AT,C,G,D]]

            metapaths = metapaths + additional_metapaths
            
        elif "hetionet" in path:
            metapaths =  metapaths#[[":" + node_type for node_type in metapath] for metapath in metapaths]
        else:
            raise ValueError("If no metapaths are specified via --metpath, then the input path specified via --input must contain the words 'hetionet' or 'drkg'.")
    else:
        metapaths = []
        with open(args.metapaths,"r") as file:
            for metapath in file:
                metapaths.append([node_type for node_type in metapath.split(",")])

    logger.debug("Metapaths that will be walked along: {}".format(metapaths))

    allTheWalks = getWalksParallel(metapaths,numWalks=5000)
    

