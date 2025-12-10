#!/bin/bash

LOADFILE="scc-sst-interconnect-workload.load"

mpirun -np X sst -n Y \
  --print-timing-info \
  --partitioner=linear \
  --model-options=" \
  --loadFile=$LOADFILE \
  --platform=hyperx \
  " \
  <path to ember directory>/test/emberLoad.py
