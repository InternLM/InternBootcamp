#!/bin/bash

set -euo pipefail

INSTRUCTION_CONFIG="${PROJECT_DIR}"
OUTPUT_DIR="${PROJECT_DIR}"

mkdir -p "${OUTPUT_DIR}"

python -m internbootcamp.utils.data_generation \
  --instruction-config "${INSTRUCTION_CONFIG}" \
  --output-dir "${OUTPUT_DIR}" \
  --split-samples train:0,test:32 \
  --shuffle \
  "$@"

echo "Generated BBEH Object Properties dataset under ${OUTPUT_DIR}"
