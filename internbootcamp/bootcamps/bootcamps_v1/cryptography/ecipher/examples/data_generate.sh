#!/bin/bash

# Ecipher数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/cryptography/ecipher/configs/Ecipher_instruction_config.yaml \
    --output-dir data/Ecipher/ \
    --split-samples train:1000,test:100 \
    --shuffle
