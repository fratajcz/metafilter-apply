# Purpose

This Repository contains the code to conduct the metapath-based filtering on knowledge graphs as described in "Task-Driven Knowledge Graph Filtering Improves Prioritizing Drugs for Repurposing" (DOI: [10.21203/rs.3.rs-721705/v1](https://doi.org/10.21203/rs.3.rs-721705/v1). . The code in this repository will walk you through the creation of the modified graph, using Hetionet and DRKG as examples. 

# Installation

...

# Usage

## Preprocessing 

First, set aside a validation and test set of edges of your desired type. These edges should not be contained in the graph file that you apply the metapath filtering on.

Second, make sure your graph is in the shape you want it to be in. If you use your only Knowledge Graph, make sure that it does not contain any ambiguous or misleading edges. For example, on DRKG, several relations between Compounds and Diseases have a "treats" character, but are worded differently. Therefore, we have added a script that unifies all these relations on DRKG (```utils/treats_edge_union.sh```).

Third, make sure that all the node types included in the graph are free of white spaces, since this will throw off several methods later on. To do this on Hetionet and DRKG, we have included a bash script that removes whitespaces from the respective entity types in these graphs (```utils/remove_whitespaces_in_node_types.sh```).

Finally, your graph has to be formatted as NetworkX object where each entity has the keyword ```label```set to the entity type that must match the entity types used in your predefined metapaths. If you have your graph in the form of an edgelist, i.e. ```tsv```, please convert it to a ```gpickle``` graph beforehand using ```utils/pickle_graph.py```. It assumes that a triple is encoded as ```head_node        relation       tail_node``` and that each node is referred to using a scheme like ```[entity_id][seperator][entity_type]```, where ```[entity_type]```is added to the entity using the ```label```keyword. This is mandatory, since these labels or entity types are used by the metapath walker to find the next entitity. Per default, ```[seperator]``` is defined as ```::```, but this can be changed using the ```--sep```argument.

## Walking.

Once your graph is in the shape you want it to be in, we can start with the walking process. Our script ```metapathWalking.py```takes the path to your graph as an argument, alongside several other arguments. You can leave most arguments on the default value, then it will recreate the conditions used in the paper.
However, you might want to change the number of concurrent walkers, depending on your machine.

an example call to the walking script might look like

```
python3 metapathWalking.py -i hetionet_train.gpickle -o walks.txt -n 1
```

to ingest the graph ```hetionet_train.gpickle```, use one concurrent walker and store the results in ```walks.txt```.

The walking script can ingest graphs of the types ```gpickle``` and ```graphml```. If you have your graph in the form of an edgelist, i.e. ```tsv```, please see the last paragraph of the Preprocessing section on how to transform you graph into an appropriate ```gpickle```file.

The walking script detects if your are using hetionet or drkg based on checking the input path that you provide, so make sure you name it appropriately. If you want to use other graphs and/or other selections of metapaths, please adjust the main method in the script by loading your own metapaths similar to the examples that you can find there, i.e.:

```
elif "your-graph-name" in path:
        metapaths = your_metapaths
```

## Filtering

After the walking process, you should have a ```walks.txt```file containing your completed walks. To filter your graph to only contain the nodes which appear in these walks, first, determine all unique nodes in the graph:

```
./process_walks.sh walks.txt
```

which will give you a file called ```unique_walks.txt``` where each line will contain one unique node identifier. Now, subset your initial graph that you used during the walking by calling

```
python3 subset_graph.py -g hetionet_train.gpickle -l unique_walks.txt -o hetionet_subset_train.tsv
```

```subset_graph.py``` can ingest graphs of the types ```gpickle```, ```graphml``` and ```tsv```. If you are using ```tsv```, make sure it has only 3 columns, which should be ```head_node  relation    tail_node```.

## Postprocessing

There is no postprocessing necessary, you can now use your original and modified versions of the graph, in our example here ```hetionet_train```and ```hetionet_subset_train```to train your favourite model and observe the differences in performance. Note that we have not made any changes to the evaluation and test sets to achieve a fair comparison. If you plan to use your edgelist in a framework that assumes edges to be directed, consider adding inverse edges where appropriate.
