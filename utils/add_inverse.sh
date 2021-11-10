#!/bin/bash

# This script adds inverse edges with suffix "_inv" to the input edgelist and outputs to stdout

awk -v OFS="\t" '{print sprintf("%s%s", $0, "\n")$3, sprintf("%s%s", $2, "_inv"), $1}' $1