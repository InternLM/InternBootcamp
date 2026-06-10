#!/bin/bash

set -euo pipefail

INSTRUCTION_CONFIG="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_geometric_shapes/configs/bbeh_geometric_shapes_instruction_config.yaml"
OUTPUT_DIR="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_geometric_shapes/data/gen"

mkdir -p "${OUTPUT_DIR}"

python -m internbootcamp.utils.data_generation \
  --instruction-config "${INSTRUCTION_CONFIG}" \
  --output-dir "${OUTPUT_DIR}" \
  --split-samples train:0,test:32 \
  --shuffle \
  "$@"

echo "Generated BBEH Geometric Shapes dataset under ${OUTPUT_DIR}"


