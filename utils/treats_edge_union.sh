#!/bin/bash

sed -e 's/\w*::\w*::Compound:Disease/union::treats::Compound:Disease/g' $1
