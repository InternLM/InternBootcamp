#!/bin/bash

# Cnetworksafety数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/cryptography/cnetworksafety/configs/Cnetworksafety_instruction_config.yaml \
    --output-dir data/Cnetworksafety/ \
    --split-samples train:1000,test:100 \
    --shuffle
