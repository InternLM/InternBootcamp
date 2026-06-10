#!/bin/bash

# Cpinkiepieeatspattycakes数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cpinkiepieeatspattycakes/configs/Cpinkiepieeatspattycakes_instruction_config.yaml \
    --output-dir data/Cpinkiepieeatspattycakes/ \
    --split-samples train:1000,test:100 \
    --shuffle
