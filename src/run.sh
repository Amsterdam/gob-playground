#!/usr/bin/env bash

if [ "$1" = "--clean" ]
then
    echo Cleaning data
    cp ./reader/original_data/* ./reader/input_data
    cp ./writer/original_data/* ./writer/data
else
    echo Run modules
    for module in "reader" "processor" "writer"
    do
        cd $module
        python main.py
        cd ..
    done
fi