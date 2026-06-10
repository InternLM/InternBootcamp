#!/bin/bash

# Candryushaandcoloredballoons数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/candryushaandcoloredballoons/configs/Candryushaandcoloredballoons_instruction_config.yaml \
    --output-dir data/Candryushaandcoloredballoons/ \
    --split-samples train:1000,test:100 \
    --shuffle
