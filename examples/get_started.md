# Quick Start

**InternBootcamp** provides functionalities such as data generation, model training, and model evaluation. You can refer to the following guide to get started quickly.

To ensure successful execution of the following steps, please make sure **InternBootcamp is installed**, and **the project root directory is set as your working directory**.

## Data Generation

Run [**run\_pipeline.sh**](examples/pipelines/run_pipeline.sh) to generate training and testing data based on the [default configuration](examples/pipelines/data_configs).
For custom configurations, please refer to the [Pipeline Usage Guide](examples/pipelines/README.md) for personalized setup.

```bash
source examples/pipelines/run_pipeline.sh
```

The generated data will be saved in the [bootcamp\_generator\_outputs directory](examples/bootcamp_generator_outputs). Each data batch is timestamped, and the directory structure is as follows:

```
examples/
├── ...
└──bootcamp_generator_outputs/
    ├── ...
    └── 2025-xx-xx-xx:xx:xx/
        ├── test/
        │   ├── bootcamp_0.jsonl
        │   ├── ...
        │   └── bootcamp_n.jsonl
        └── train/
            ├── bootcamp_0.jsonl
            ├── ...
            └── bootcamp_n.jsonl
```

## Model Training(Reinforcement learning)

We provide support for two training frameworks: **Xpuyu** and **Verl**.

### Xpuyu

Refer to the [Xpuyu documentation](examples/xpuyu_usage/README.md) to get started with efficient training.

### Verl

To integrate Bootcamp tasks into the Verl framework for training, you need to embed the Bootcamp reward computation method into Verl.
See the [Verl documentation](examples/verl_usage/README.md) for detailed guidance.

## Model Evaluation

For Bootcamp tasks, we offer a customized evaluation service.
Once the model to be evaluated is deployed using frameworks like FastChat or Ollama, and you have the corresponding API URL and API Key, you can run the following command to evaluate your deployed model on the **InternBootcamp\_eval** dataset:

```bash
cd InternBootcamp
python examples/unittests/run_eval.py \
    --url http://127.0.0.1:8000/v1 \
    --api_key EMPTY \
    --model_name r1_32B \
    --api_mode completion \
    --template r1 \
    --max_tokens 32768 \
    --temperature 0 \
    --test_dir examples/data/InternBootcamp_eval \
    --max_concurrent_requests 128 \
    --timeout 6000 \
    --max_retries 16 \
    --max_retrying_delay 60
```

**Note:** When `api_mode` is set to `completion`, be sure to correctly specify the corresponding template (supported: `r1`, `qwen`, `internthinker`, `chatml` (with no system prompt)).
For more detailed instructions, refer to the [Evaluation Manual](examples/unittests/README.md).

---

Let me know if you’d like a version with clearer formatting for publishing or documentation.
