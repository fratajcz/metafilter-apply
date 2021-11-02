#!/bin/bash

sed -e 's/Biological Process/BiologicalProcess/g' $1 > $1_no_whitespace
sed -i -e  's/Cellular Component/CellularComponent/g' $1_no_whitespace
sed -i -e  's/Molecular Function/MolecularFunction/g' $1_no_whitespace
sed -i -e  's/Pharmacologic Class/PharmacologicClass/g' $1_no_whitespace
sed -i -e  's/Side Effect/SideEffect/g' $1_no_whitespace

