#!/bin/bash

# Feuclidsnightmare数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/feuclidsnightmare/configs/Feuclidsnightmare_instruction_config.yaml \
    --output-dir data/Feuclidsnightmare/ \
    --split-samples train:1000,test:100 \
    --shuffle
