# run on 8xH100
# make sure your current working directory is the root of the project

set -x

ulimit -n 65535
PROJECT_DIR="$(pwd)"
MODEL_PATH="${PROJECT_DIR}"
CONFIG_PATH="${PROJECT_DIR}"
CONFIG_NAME="amplifier_multiturn_grpo"
TOOL_CONFIG_PATH="${PROJECT_DIR}"
DATA_TRAIN_FILE_PATH="${PROJECT_DIR}"
DATA_VAL_FILE_PATH="${PROJECT_DIR}"
PROJECT_NAME="test"
EXPERIMENT_NAME="test"

python -m verl.trainer.main_ppo \
    --config-path="$CONFIG_PATH" \
    --config-name="$CONFIG_NAME" \
    trainer.default_hdfs_dir=null \
    trainer.default_local_dir=$PROJECT_DIR/ckpts/$EXPERIMENT_NAME\_\${now:%Y-%m-%d} \
    trainer.rollout_data_dir=$PROJECT_DIR/ckpts/$EXPERIMENT_NAME\_\${now:%Y-%m-%d}/rollout \
    algorithm.adv_estimator=grpo \
    data.train_batch_size=32 \
    data.max_prompt_length=1600 \
    data.max_response_length=1024 \
    data.filter_overlong_prompts=True \
    data.truncation='left' \
    data.return_raw_chat=True \
    actor_rollout_ref.model.path=$MODEL_PATH \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=32 \
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
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=4 \
    actor_rollout_ref.rollout.prompt_length=1600 \
    actor_rollout_ref.rollout.response_length=1024 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console"]' \
    trainer.project_name=$PROJECT_NAME \
    trainer.experiment_name=$EXPERIMENT_NAME \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=20 \
    data.train_files=$DATA_TRAIN_FILE_PATH \
    data.val_files=$DATA_VAL_FILE_PATH \
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \
    trainer.total_epochs=15 $@

