#!/bin/bash

pycc_usage="$(basename "$0") [-h] model_file predict_n_characters -- Start PyCodeComplete WebApp

where:
    -h  show this help text
    model_file  Serialized RNN Model
    predict_n_characters Number of characters to predict"


while getopts ':h' opt; do
    case $opt in
        h)  echo "$pycc_usage"
            exit
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            echo "$pycc_usage"
            exit
            ;;
    esac
done

if [ -z "$1" ]
  then
    echo "No RNN Model file supplied"
    echo "$pycc_usage"
    exit
fi

if [ -z "$2" ]
  then
    echo "Number of characters to predict not supplied"
    echo "$pycc_usage"
    exit
fi

python -m webapp.app $1 $2
