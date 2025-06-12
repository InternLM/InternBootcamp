# 使用 Xtuner 进行 Bootcamp 训练

## 🚄 训练教程

### 1. 安装依赖项

我们使用 [XTuner](https://github.com/InternLM/xtuner/tree/main) 作为训练引擎。

您需要确保 InternBootcamp 已成功安装。

```bash
pip install -e $InternBootcamp_path
```

然后安装 xtuner 及其依赖项。

```bash
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124  
pip install flash-attn --no-build-isolation
pip install xtuner[all]==0.2.0rc0
```

### 2. 准备数据

可以通过 `examples/xpuyu_usage/xpuyu_data_preprocess.py` 将 bootcamp 数据转换为训练格式。

**示例用法：**
```python
python examples/xpuyu_usage/xpuyu_preprocess.py --src examples/bootcamp_generator_outputs/{%Y-%m-%d-%H:%M:%S}
```

### 3. 准备您的训练配置

准备您的训练配置以开始 GRPO 训练。

一个示例配置文件位于：

```bash
examples/xpuyu_usage/bootcamp_rl/configs/example_training_config.py
```

### 4. 开始训练

```bash
cd examples/xpuyu_usage

GPUS_PER_NODE=$(python -c 'import torch; print(torch.cuda.device_count())')

# GPU 工作节点的数量，如果是单工作节点训练，请设置为 1
NNODES=${WORLD_SIZE:-1} # 修改以适应集群环境

# 当前工作节点的编号，应为 {0, ..., WORKER_CNT-1} 中的值，如果是单工作节点训练，请设置为 0
NODE_RANK=${RANK:-0} # 修改以适应集群环境

# Rank-0 工作节点的 IP 地址，如果是单工作节点训练，请设置为 localhost
MASTER_ADDR=${MASTER_ADDR:-localhost}

# 通信端口
MASTER_PORT=${MASTER_PORT:-6001}

DISTRIBUTED_ARGS="
    --nproc_per_node $GPUS_PER_NODE \
    --nnodes $NNODES \
    --node_rank $NODE_RANK \
    --master_addr $MASTER_ADDR \
    --master_port $MASTER_PORT
"

echo $DISTRIBUTED_ARGS

torchrun $DISTRIBUTED_ARGS train_grpo.py ./bootcamp_rl/configs/example_training_config.py --work_dir examples/xpuyu_usage/ckpts/experiment_name
```

### 5. 训练曲线可视化

您可以使用 `examples/xpuyu_usage/report_to_wandb.py` 来可视化训练曲线。

```bash
python examples/xpuyu_usage/report_to_wandb.py examples/xpuyu_usage/ckpts/{experiment_name}/{timestamp}/rank0.log.jsonl {wandb_project_name}
```