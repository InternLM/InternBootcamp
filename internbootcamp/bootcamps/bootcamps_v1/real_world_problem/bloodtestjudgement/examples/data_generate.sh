#!/bin/bash

# Bloodtestjudgement数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/real_world_problem/bloodtestjudgement/configs/BloodTestJudgement_instruction_config.yaml \
    --output-dir data/BloodTestJudgement/ \
    --split-samples train:1000,test:100 \
    --shuffle
