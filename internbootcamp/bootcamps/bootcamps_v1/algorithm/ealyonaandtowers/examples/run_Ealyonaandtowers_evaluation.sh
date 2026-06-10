#!/bin/bash

# Ealyonaandtowers评估脚本

API_KEY=sk-xxxx
API_URL=https://api.openai.com/v1
API_MODEL=gpt-3.5-turbo

python -m internbootcamp.utils.run_evaluation \
    --dataset-path data/Ealyonaandtowers/20250814153842_test.jsonl \
    --output-dir data/Ealyonaandtowers/Ealyonaandtowers_evaluation/ \
    --api-key "$API_KEY" \
    --api-url "$API_URL" \
    --api-model "$API_MODEL" \
    --reward-calculator-class "internbootcamp.bootcamps.bootcamps_v1.algorithm.ealyonaandtowers.Ealyonaandtowers_reward_calculator.EalyonaandtowersRewardCalculator" \
    --tool-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ealyonaandtowers/configs/Ealyonaandtowers_tool_config.yaml \
    --interaction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ealyonaandtowers/configs/Ealyonaandtowers_interaction_config.yaml \
    --max-tool-turns-per-interaction 5 \
    --max-interaction-turns 3 \
    --max-concurrent 16
