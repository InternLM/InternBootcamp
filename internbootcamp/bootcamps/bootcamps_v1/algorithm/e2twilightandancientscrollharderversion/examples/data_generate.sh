#!/bin/bash

# E2twilightandancientscrollharderversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/e2twilightandancientscrollharderversion/configs/E2twilightandancientscrollharderversion_instruction_config.yaml \
    --output-dir data/E2twilightandancientscrollharderversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
