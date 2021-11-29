# Purpose

This Repository contains the code to conduct the metapath-based filtering on knowledge graphs as described in "Task-Driven Knowledge Graph Filtering Improves Prioritizing Drugs for Repurposing" (DOI: [10.21203/rs.3.rs-721705/v1](https://doi.org/10.21203/rs.3.rs-721705/v1)).  The code in this repository will walk you through the creation of a modified graph, using Hetionet and DRKG as examples. 

If you just want to run the experiments or use the datasets mentioned in the paper, you can find the datasets ready-to-use [here](https://doi.org/10.5281/zenodo.5638999) and the code to run the experiments [here](https://github.com/fratajcz/metafilter-experiment) .

# Installation

The code in this repo was developed and tested on CentOS Linux 7.9 and Ubuntu 18.04 LTS.

To set up the necessary environment to run the code we suggest the user to use [Anaconda](https://www.anaconda.com/).

Install the necessary conda env by using:

```
conda env create -f environment.yml
```

Or install the packages that are mentioned in ```environment.yml```manually.

# Usage

## Quickstart

To allow a quick testrun and provide a high-level wrapper we have compiled ```full_pipeline.py```which gives you access to all individual scripts' arguments.
Since the pipeline differs if the graph should be used as a whole (i.e. because a holdout set is already created) or if train/val/test splitting should to be performed by the pipeline, we give two examples on an extremely reduce version of hetionet. Bear in mind that this only serves as a minimal working example and does not generate meaningful results!

### No Splitting
```
python3 full_pipeline.py --input data/hetionet_train_toy.txt  -o hetionet_train_toy_subset.txt -p data/metapaths_toy.txt -n 4 -w 1 -s 1
```
This is a minimal working example which runs through the whole process and should finish within a few minutes. It produces a logfile ```run.log``` which contains minute details of the run. This run walks four metapaths (given in ```data/metapaths_toy.txt```), each with its own concurrent walker (```-n 4```), starting once on every node (```-s 1```) and producing one concatenated walk per metapath (```-w 1```). Note that you might see a warning that the walks could not be concatenated for some metapaths since we sample only very few short walks in this example. Thats why the default parameters are ```-w 5000 -s 1000```.

The result is then stored in ```hetionet_train_toy_subset.txt```.


### Perform train/val/test split internally
```
python3 full_pipeline.py --input data/hetionet_full_toy.txt -p data/metapaths_toy.txt -n 4 -w 1 -s 1 -x 0.2
```

The additional flag ```-x 0.2``` triggers the internal train/val/test split, setting 20% of treats-edges aside, 10% for validation and 10% for test. 
After walking and modifying the graph, ```utils/delete_disconnected.py```is run automatically and makes sure that nodes that are removed in the modification process are also removed from the test and validation set. Note that, since this is only a minimal working example, this might remove all edges from the test and validation set.

If you use internal splitting, the method will always produce the files ```train.txt```,```train_subset.txt```,```valid.txt```,```test.txt```,```valid_cleaned.txt```,```test_cleaned.txt```, no matter what you specify as output file. ```train.txt``` is the training set from the original graph, ```train_subset.txt``` is the modified training set and the cleaned val and test sets should be used for validation and testing.

These examples should give you an impression on how to apply the metapath based filtering method on your own dataset. For more details, continue reading.

## Preprocessing 

First, make sure your graph is in the shape you want it to be in. If you use your own Knowledge Graph, make sure that it does not contain any ambiguous or misleading edges. For example, on DRKG, several relations between Compounds and Diseases have a "treats" character, but are worded differently. Therefore, we have added a script that unifies all these relations on DRKG (```utils/treats_edge_union.sh```). Feel free to adapt that script to your own needs. Also, your graph should not yet contain inverse edges, as this would create very easy to predict holdout samples in the next step and potentially also influence the walking process! Add these inverse edges in the very last step if you need them.

Second, set aside a validation and test set of edges of your desired type. These edges should not be contained in the graph file that you apply the metapath filtering on. You can use your own script to do this, use your prestratified dataset right away or use the python script ```utils/split.py``` to achieve this. For the documentation of the script, run it with the ```-h```parameter.

Third, make sure that all the node types included in the graph are free of white spaces, since this will throw off several methods later on. To do this on Hetionet and DRKG, we have included a bash script that removes whitespaces from the respective entity types in these graphs (```utils/remove_whitespaces_in_node_types.sh```). If your graph contains different entity types, feel free to modify this script.

Finally, your graph has to be formatted as a NetworkX object where each entity has the keyword ```label``` set to the entity type that must match the entity types used in your predefined metapaths. If you have your graph in the form of an edgelist, i.e. ```tsv```, please convert it to a ```gpickle``` graph beforehand using ```utils/pickle_graph.py```. It assumes that a triple is encoded as ```head_entity        relation       tail_entity``` and that each entity is referred to using a scheme like ```[entity_type][seperator][entity_id]```, where ```[entity_type]```is added to the entity in the Networkx graph object using the ```label```keyword. Per default, ```[seperator]``` is defined as ```::```, but this can be changed using the ```--sep```argument. For example, if the entity is referred to as ```Compound::DOID:1324```, then ```Compound```will be used as the entity's type. This is mandatory, since these labels or entity types are used by the metapath walker to find the next entitity. 

## Walking.

Once your graph is in the shape you want it to be in, we can start with the walking process. Our script ```metapathWalking.py```takes the path to your graph as an argument, alongside several other arguments. You can leave most arguments on the default value, then it will recreate the conditions used in the paper.
However, you might want to change the number of concurrent walkers, depending on your machine.

an example call to the walking script might look like

```
python3 metapathWalking.py -i hetionet_train.gpickle -o walks.txt -n 1
```

to ingest the graph ```hetionet_train.gpickle```, use one concurrent walker and store the results in ```walks.txt```. We encourage the user to us emore than one concurrent walker, otherwise this step takes very long. Since every walker uses one CPU has its own copy of the graph in memory, the optimal number of walkers depends on the CPU and memory specs of the users machine.

The walking script can ingest graphs of the types ```gpickle``` and ```graphml```. If you have your graph in the form of an edgelist, i.e. ```tsv```, please see the last paragraph of the Preprocessing section on how to transform your graph into an appropriate ```gpickle```file.

The walking script detects if your are using hetionet or drkg based on checking the input path that you provide, so make sure you name it appropriately. If you want to use other graphs and/or other selections of metapaths, please provide them in comma seperated fashion, one metapath per line, via the argument ```-p``` (see Quickstart example).

## Filtering

After the walking process, you should have a ```walks.txt```file containing your completed walks. To filter your graph to only contain the nodes which appear in these walks, first, determine all unique nodes in the walks that you just produced:

```
./process_walks.py --input walks.txt --output unique_ids.txt
```

which will give you a file called ```unique_walks.txt``` where each line will contain one unique node identifier. Now, subset your initial graph that you used during the walking by calling

```
python3 subset_graph.py -g hetionet_train.gpickle -l unique_ids.txt -o hetionet_subset_train.tsv
```

```subset_graph.py``` can ingest graphs of the types ```gpickle```, ```graphml``` and ```tsv```. If you are using ```tsv```, make sure it has only 3 columns, which should be ```head_entity  relation    tail_entity```.

## Postprocessing

Before you start training you ML models on the original and modified version, make sure that your test and validation sets do not contain edges whose incident compound and diseases entities have been deleted during subsetting. This is necessary to make sure that you evaluate your performance on congruent test and validation sets. To achieve this, we provide a script called ```delete_disconnected.py```which you can use as follows:

```
python3 utils/delete_disconnected.py -i hetionet_subset_train.txt -t test.txt -v valid.txt
```

This will yield the new test and validation edge lists ```cleaned_test.tsv``` and ```cleaned_val.tsv```and report on how many edges have been removed.


There is no further postprocessing necessary, you can now use your original and modified versions of the graph, in our example here ```hetionet_train```and ```hetionet_subset_train```to train your favourite model and observe the differences in performance on the holdout sets. If you plan to use your edgelist in a framework that assumes edges to be directed, consider adding inverse edges where appropriate. You can use the script ```utils/add_inverse.sh```and store the result in a new file. Now you are ready and set to run some [experiments](https://github.com/fratajcz/metafilter-experiment).


