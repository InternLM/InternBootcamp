#!/bin/bash

# Korlogiccanonicalpropositions数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/korlogiccanonicalpropositions/configs/korLogicCanonicalPropositions_instruction_config.yaml \
    --output-dir data/korLogicCanonicalPropositions/ \
    --split-samples train:1000,test:100 \
    --shuffle
