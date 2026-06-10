#!/bin/bash

set -euo pipefail

INSTRUCTION_CONFIG="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_buggy_tables/configs/bbeh_buggy_tables_instruction_config.yaml"
OUTPUT_DIR="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_buggy_tables/data/gen"

mkdir -p "${OUTPUT_DIR}"

python -m internbootcamp.utils.data_generation \
  --instruction-config "${INSTRUCTION_CONFIG}" \
  --output-dir "${OUTPUT_DIR}" \
  --split-samples train:0,test:32 \
  --shuffle \
  "$@"

echo "Generated BBEH Buggy Tables dataset under ${OUTPUT_DIR}"


