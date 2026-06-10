#!/bin/bash
set -e

# 从项目根目录运行
cd "$(dirname "$0")"/../../../..

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/fenics_bootcamp/configs/fenics_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/fenics_bootcamp/data/fenics_bootcamp/ \
    --split-samples train:0,test:100 \
    --shuffle
