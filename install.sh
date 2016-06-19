#!/bin/bash

script_dir=$(cd $(dirname $(readlink -f $0 || echo $0));pwd -P)
for i in nautilus-scripts/*
do
    ln -sf $script_dir/$i $HOME/.local/share/nautilus/scripts/
done
