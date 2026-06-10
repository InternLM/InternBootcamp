# Stopped maintenance

set -x

ulimit -n 65535

PROJECT_DIR="${PROJECT_DIR}"  
MODEL_PATH="${PROJECT_DIR}"
model_name="Qwen2.5-1.5B"
verl_bootcampv2_dir="${PROJECT_DIR}"
CONFIG_PATH="${verl_bootcampv2_dir}/internbootcamp/bootcamps/example_bootcamp/configs/"
CONFIG_NAME="example_multiturn_w_tool_grpo"  
TOOL_CONFIG_PATH="${verl_bootcampv2_dir}/internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config_with_server_urls.yaml"  
DATA_TRAIN_FILE_PATH="${PROJECT_DIR}/data/example_arithmetic/20250808112600_train.parquet"  
DATA_VAL_FILE_PATH="${PROJECT_DIR}/data/example_arithmetic/20250808112600_test.parquet"  

PROJECT_NAME="bootcampv2"  
EXPERIMENT_NAME="example_bootcamp_arithmetic_grpo_${model_name}"
TIMESTAMP=$(date +%Y-%m-%d)

cd "$verl_bootcampv2_dir" || exit 1

python -m verl.trainer.main_ppo \
    --config-path="$CONFIG_PATH" \
    --config-name="$CONFIG_NAME" \
    trainer.default_hdfs_dir=null \
    trainer.default_local_dir=$PROJECT_DIR/ckpts/$EXPERIMENT_NAME\_$TIMESTAMP \
    trainer.rollout_data_dir=$PROJECT_DIR/ckpts/$EXPERIMENT_NAME\_$TIMESTAMP/rollout \
    algorithm.adv_estimator=grpo \
    data.train_batch_size=16 \
    data.max_prompt_length=4096 \
    data.max_response_length=1024 \
    data.filter_overlong_prompts=True \
    data.truncation='left' \
    data.return_raw_chat=True \
    actor_rollout_ref.model.path=$MODEL_PATH \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=16 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
    actor_rollout_ref.rollout.name=sglang \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.75 \
    actor_rollout_ref.rollout.n=4 \
    actor_rollout_ref.rollout.prompt_length=8192 \
    actor_rollout_ref.rollout.response_length=1024 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console"]' \
    trainer.project_name=$PROJECT_NAME \
    trainer.experiment_name=$EXPERIMENT_NAME \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=2 \
    data.train_files=$DATA_TRAIN_FILE_PATH \
    data.val_files=$DATA_VAL_FILE_PATH \
    trainer.val_before_train=False \
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \
    reward_model.reward_manager=bootcamp \
    +reward_model.reward_kwargs.format_score=0 \
    +reward_model.reward_kwargs.short_penalty=False \
    +reward_model.reward_kwargs.short_threshold=512 \
    +reward_model.reward_kwargs.think_threshold=0 \
    +reward_model.reward_kwargs.ans_threshold=256 \
    +reward_model.reward_kwargs.format_penalty=False \
    +reward_model.reward_kwargs.parallel_workers=1 \
    trainer.total_epochs=15 "$@"

