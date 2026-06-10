#!/bin/bash

# Galaxies数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/galaxies/configs/galaxies_instruction_config.yaml \
    --output-dir data/galaxies/ \
    --split-samples train:1000,test:100 \
    --shuffle
