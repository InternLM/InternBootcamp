#!/bin/bash

# Korciphercustominverseshiftsubstitutioncipher数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/cryptography/korciphercustominverseshiftsubstitutioncipher/configs/korCipherCustomInverseShiftSubstitutionCipher_instruction_config.yaml \
    --output-dir data/korCipherCustomInverseShiftSubstitutionCipher/ \
    --split-samples train:1000,test:100 \
    --shuffle
