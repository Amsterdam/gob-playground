#!/usr/bin/env bash

if [ "$1" = "--clean" ]
then
    echo Cleaning data
    cp ./reader/original_data/* ./reader/input_data
    rm ./reader/output_data/*
    rm ./processor/output_data/*
    cp ./writer/original_data/* ./writer/data
    rm ./api/output_data/*
    rm ./export/output_data/*
elif [ "$1" != "" ]
then
    MODULE=$1
    echo Run $MODULE
    cd $MODULE
    python main.py
else
    echo Run modules
    for module in "reader" "processor" "writer" "api" "export"
    do
        cd $module
        python main.py
        cd ..
    done
fi