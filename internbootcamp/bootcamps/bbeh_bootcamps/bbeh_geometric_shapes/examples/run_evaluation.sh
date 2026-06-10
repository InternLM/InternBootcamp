#!/bin/bash

set -euo pipefail

DATASET="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_geometric_shapes/data/gen/bbeh_geometric_shapes_20251110165439_test.jsonl"

OUTPUT_DIR="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_geometric_shapes/data/eval_outputs"
API_KEY="${API_KEY:-sk-xxxx}"
API_URL="${API_URL:-http://100.103.25.14:21003/v1}"
API_MODEL="${API_MODEL:-qwen3-30b-a3b-instruct-2507}"

REWARD_CALCULATOR_CLASS="internbootcamp.bootcamps.bbeh_bootcamps.bbeh_geometric_shapes.reward_calculator.BbehGeometricShapesRewardCalculator"
INTERACTION_CONFIG="internbootcamp/bootcamps/bbeh_bootcamps/bbeh_geometric_shapes/configs/bbeh_geometric_shapes_interaction_config.yaml"
EVALUATOR_CLASS="internbootcamp.src.base_evaluator.BaseEvaluator"

MAX_ASSISTANT_TURNS=${MAX_ASSISTANT_TURNS:-1}
MAX_USER_TURNS=${MAX_USER_TURNS:-32}
MAX_CONCURRENT=${MAX_CONCURRENT:-64}

mkdir -p "${OUTPUT_DIR}"

python -m internbootcamp.utils.run_evaluation \
  --dataset-path "${DATASET}" \
  --output-dir "${OUTPUT_DIR}" \
  --api-key "${API_KEY}" \
  --api-url "${API_URL}" \
  --api-model "${API_MODEL}" \
  --evaluator-class "${EVALUATOR_CLASS}" \
  --reward-calculator-class "${REWARD_CALCULATOR_CLASS}" \
  --interaction-config "${INTERACTION_CONFIG}" \
  --max-assistant-turns "${MAX_ASSISTANT_TURNS}" \
  --max-user-turns "${MAX_USER_TURNS}" \
  --max-concurrent "${MAX_CONCURRENT}" \
  --api-extra-params '{"temperature":0.6,"max_completion_tokens":32768}' \
  --verify-correction-kwargs '{"format_penalty": false}' \
  --verbose

echo "Evaluation finished. Results saved under ${OUTPUT_DIR}"


