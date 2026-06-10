#!/bin/bash

# Bjohnnyandgrandmaster评估脚本

API_KEY=sk-xxxx
API_URL=https://api.openai.com/v1
API_MODEL=gpt-3.5-turbo

python -m internbootcamp.utils.run_evaluation \
    --dataset-path data/Bjohnnyandgrandmaster/20250814153842_test.jsonl \
    --output-dir data/Bjohnnyandgrandmaster/Bjohnnyandgrandmaster_evaluation/ \
    --api-key "$API_KEY" \
    --api-url "$API_URL" \
    --api-model "$API_MODEL" \
    --reward-calculator-class "internbootcamp.bootcamps.bootcamps_v1.algorithm.bjohnnyandgrandmaster.Bjohnnyandgrandmaster_reward_calculator.BjohnnyandgrandmasterRewardCalculator" \
    --tool-config internbootcamp/bootcamps/bootcamps_v1/algorithm/bjohnnyandgrandmaster/configs/Bjohnnyandgrandmaster_tool_config.yaml \
    --interaction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/bjohnnyandgrandmaster/configs/Bjohnnyandgrandmaster_interaction_config.yaml \
    --max-tool-turns-per-interaction 5 \
    --max-interaction-turns 3 \
    --max-concurrent 16
