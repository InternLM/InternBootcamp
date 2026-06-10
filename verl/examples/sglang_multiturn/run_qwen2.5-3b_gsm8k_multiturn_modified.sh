# run on 8xH100
# make sure your current working directory is the root of the project

# set -x

# 这个模型不能够开sequence parallel 会报错

ulimit -n 65535

export http_proxy=http://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:13128 && export https_proxy=https://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:13128 && export HTTP_PROXY=https://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:13128 && export HTTPS_PROXY=https://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:13128

project_name='gsm8k_async_rl'
experiment_name='qwen2.5-3b_function_rm-gsm8k-sgl-multi-w-tool-verify-n16'
PROJECT_DIR="$(pwd)"
CONFIG_PATH="$PROJECT_DIR/examples/sglang_multiturn/config"
TOOL_CONFIG_PATH=$PROJECT_DIR/examples/sglang_multiturn/config/tool_config/gsm8k_tool_config.yaml
export VERL_PPO_LOGGING_LEVEL=DEBUG
export HYDRA_FULL_ERROR=1
export WANDB_API_KEY="350272d1b727788703b1f5d46518d3c1f41b274f"

mkdir -p $PROJECT_DIR/ckpts

train_files="['$PROJECT_DIR/data/gsm8k/train.parquet']"
test_files="['$PROJECT_DIR/data/gsm8k/test.parquet']"

# python 而不能是python3
python -m verl.trainer.main_ppo \
    --config-path="$CONFIG_PATH" \
    --config-name='gsm8k_multiturn_grpo' \
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \
    algorithm.adv_estimator=grpo \
    data.train_batch_size=256 \
    data.max_prompt_length=1024 \
    data.max_response_length=1024 \
    data.filter_overlong_prompts=True \
    data.truncation='left' \
    data.return_raw_chat=True \
    actor_rollout_ref.model.path=${PROJECT_DIR} \
    trainer.default_hdfs_dir=null \
    trainer.default_local_dir=$PROJECT_DIR/ckpts/$experiment_name \
    trainer.rollout_data_dir=$PROJECT_DIR/ckpts/$experiment_name/rollout \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=256 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=32 \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.grad_clip=1.0 \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.loss_agg_mode=seq-mean-token-mean \
    actor_rollout_ref.actor.kl_loss_coef=0.0 \
    actor_rollout_ref.actor.clip_ratio_low=0.2 \
    actor_rollout_ref.actor.clip_ratio_high=0.28 \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=32 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
    actor_rollout_ref.rollout.name=sglang \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=16 \
    actor_rollout_ref.rollout.temperature=1 \
    actor_rollout_ref.rollout.top_p=0.9 \
    actor_rollout_ref.rollout.top_k=-1 \
    actor_rollout_ref.rollout.enable_chunked_prefill=True \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    algorithm.use_kl_in_reward=False \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=32 \
    trainer.critic_warmup=0 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name=$project_name \
    trainer.experiment_name=$experiment_name \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=5 \
    data.train_files="$train_files" \
    data.val_files="$test_files" \
    trainer.val_before_train=False \
    trainer.total_epochs=15 \
    actor_rollout_ref.rollout.update_weights_bucket_megabytes=512 $@

