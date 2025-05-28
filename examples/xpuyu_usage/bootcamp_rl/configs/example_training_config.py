# Automatic Generated Configs

# Model Related Settings
actor="actor_model_path"
reference="actor_model_path"
chat_template="r1"
dtype="auto"
selective_recompute=1.0
cpu_offload=False
cuda_graph=True
tp_size=4
sp_size=1

# Dataset Related Settings
datasets="your dataset path"
data_difficulty_balance_cfg=None
num_workers=0

# Generate Related Settings
gen_global_batch=128
gen_max_new=8192
gen_max_length=10240
gen_top_k=0
gen_top_p=0.9
temperature=1
gen_do_sample=True
max_prefill_batch=8
prompt_repeat_k=4

# Optimizer Related Settings
rl_global_batch=128
rl_micro_batch=4
rl_mini_batch_steps=1
warmup_steps=0
actor_lr=1e-6
actor_min_lr=1e-6
wd=0.01
max_grad_norm=1

# General Settings
work_dir="examples/xpuyu_usage/ckpts/experiment_name"
checkpoint_interval=40
log_interval=1
seed=0
debug=True

# Reward Settings
reward_shaping_type="grpo"
loss_type="per_token"
kl_coef=0.01
stop_word="<｜end▁of▁sentence｜>"


judgers_config = dict(
    bootcamp_judger=dict(  
        stop_word=stop_word,
        num_processes=8,
        concurrency_per_proc=(8, 8),
    ),
)

import json
data_judger_mapping = {}

with open("dataset_path", "r") as f:
    for line in f:
        item = json.loads(line)
        data_judger_mapping[item["metadata"]["data_source"]] = ["bootcamp_judger"]


