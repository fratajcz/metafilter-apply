#!/bin/bash
#
# This script takes a walkfile (nodes space seperated, each walk newline seperated), puts each occuring node in its own line, keeping only unique nodes.


#for drkg (space seperated):
cp $1 tmp
sed -i -e 's/ /\n/g' tmp
sort tmp | uniq > unique_$1
rm tmp