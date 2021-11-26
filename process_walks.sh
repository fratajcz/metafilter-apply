#!/bin/bash
#
# This script takes a walkfile (nodes space seperated, each walk newline seperated), puts each occuring node in its own line, keeping only unique nodes.


#space seperated:
cp $1 tmp
sed -i -e 's/ /\n/g' tmp
sort tmp --parallel $2 | uniq > unique_$1
rm tmp