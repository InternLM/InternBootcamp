#!/bin/bash

# Korpuzzlecryptomath数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/character_puzzles/korpuzzlecryptomath/configs/korPuzzleCryptoMath_instruction_config.yaml \
    --output-dir data/korPuzzleCryptoMath/ \
    --split-samples train:1000,test:100 \
    --shuffle
