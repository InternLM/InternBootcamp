#!/bin/bash

# Cmishaandforest数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/cmishaandforest/configs/Cmishaandforest_instruction_config.yaml \
    --output-dir data/Cmishaandforest/ \
    --split-samples train:1000,test:100 \
    --shuffle
