#!/bin/bash

# Cpredictoutcomeofthegame数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cpredictoutcomeofthegame/configs/Cpredictoutcomeofthegame_instruction_config.yaml \
    --output-dir data/Cpredictoutcomeofthegame/ \
    --split-samples train:1000,test:100 \
    --shuffle
