#!/bin/bash

# Bbehgeometricshapes数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/bbehgeometricshapes/configs/BbehGeometricShapes_instruction_config.yaml \
    --output-dir data/BbehGeometricShapes/ \
    --split-samples train:1000,test:100 \
    --shuffle
