#!/bin/bash

# Cmarinaandvasya数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/character_puzzles/cmarinaandvasya/configs/Cmarinaandvasya_instruction_config.yaml \
    --output-dir data/Cmarinaandvasya/ \
    --split-samples train:1000,test:100 \
    --shuffle
