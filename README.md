# Purpose

This Repository contains the code to conduct the metapath-based filtering on knowledge graphs as described in "..." by "...". The code in this repository will walk you through the creation of the modified graph, using Hetionet and DRKG as examples. 

# Installation

...

# Usage

## Preprocessing 

First, set aside a validation and test set of edges of your desired type. These edges should not be contained in the graph file that you apply the metapath filtering on.

Second, make sure your graph is in the shape you want it to be in. If you use your only Knowledge Graph, make sure that it does not contain any ambiguous or misleading edges. For example, on DRKG, several relations between Compounds and Diseases have a "treats" character, but are worded differently. Therefore, we have added a script that unifies all these relations on DRKG (```utils/treats_edge_union.sh```).

Third, make sure that all the node types included in the graph are free of white spaces, since this will throw off several methods later on. TO do this on Hetionet and DRKG, we have included a bash script that removes whitespaces from the respective entity types in these graphs (```utils/remove_whitespaces_in_node_types.sh```).

## Walking.

Once your graph is in the shape you want it to be in, we can start with the walking process. Our script ```metapathWalking.py```takes the path to your graph as an argument, alongside several other arguments. You can leave most arguments on the default value, then it will recreate the conditions used in the paper.
However, you might want to change the number of concurrent walkers, depending on your machine.

an example call to the walking script might look like

```
python3 metapathWalking.py -i hetionet_train.gpickle -o walks.txt -n 1
```

to ingest the graph ```hetionet_train.gpickle```, use one concurrent walker and store the results in ```walks.txt```.
The script can ingest graphs of the types ```gpickle``` and ```graphml```. 
I your graph is formatted as a ```tsv```edgelist, consider formatting it as a ```gpickle```along the lines of our ```utils/pickle_graph.py```script, which is a faster and more compact binary file format for graphs.

The script detects if your are using hetionet or drkg based on checking the input path that you provide, so make sure you name it appropriately. If you want to use other graphs and/or other selections of metapaths, please adjust the main method in the script by loading your own metapaths similar to the examples that you can find there, i.e.:

```
elif "your-graph-name" in path:
        metapaths = your_metapaths
```

## Filtering

After the walking process, you should have a ```walks.txt```file containing your completed walks. To filter your graph to only contain the nodes which appear in these walks, first, determine all unique nodes in the graph:

```
./process_walks.sh walks.txt
```

which will give you a file called ```unique_walks.txt```where each line will contain one unique node identifier per line. Now, subset your initial graph that you used during the walking by calling

```
python3 subset_graph.py -g hetionet_train.gpickle -l unique_walks.txt -o hetionet_subset_train.gpickle
```

```subset_graph.py``` can also handle tsv files, so you can instead ingest you original, tab-seperated edgelist instead of the pickled graph.

## Postprocessing

If you want to use your modified graph in a context where you need it as an edgelist, i.e. a tsv-file, you can use our script ```utils/unpickle_graph.py```to create edgelists again.
