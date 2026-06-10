#!/bin/bash

# Cphoenixanddistribution数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cphoenixanddistribution/configs/Cphoenixanddistribution_instruction_config.yaml \
    --output-dir data/Cphoenixanddistribution/ \
    --split-samples train:1000,test:100 \
    --shuffle
