#!/bin/bash

set -euo pipefail

INSTRUCTION_CONFIG="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_hyperbaton/configs/bbeh_hyperbaton_instruction_config.yaml"
OUTPUT_DIR="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_hyperbaton/data/gen"

mkdir -p "${OUTPUT_DIR}"

python -m internbootcamp.utils.data_generation \
  --instruction-config "${INSTRUCTION_CONFIG}" \
  --output-dir "${OUTPUT_DIR}" \
  --split-samples train:0,test:64 \
  --shuffle \
  "$@"

echo "Generated BBEH Hyperbaton dataset under ${OUTPUT_DIR}"


