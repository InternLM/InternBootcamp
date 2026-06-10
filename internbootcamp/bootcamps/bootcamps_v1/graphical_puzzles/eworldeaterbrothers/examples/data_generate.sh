#!/bin/bash

# Eworldeaterbrothers数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/eworldeaterbrothers/configs/Eworldeaterbrothers_instruction_config.yaml \
    --output-dir data/Eworldeaterbrothers/ \
    --split-samples train:1000,test:100 \
    --shuffle
