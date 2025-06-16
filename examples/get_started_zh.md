# 快速开始
InternBootcamp提供了数据生成、模型训练、模型评测等功能，可参考如下指南快速入门。
为确保后续操作成功执行，请确保您已经安装了InternBootcamp，并将项目根目录设为工作目录。
## 数据生成

运行[**run_pipeline.sh**](examples/pipelines/run_pipeline.sh)即可根据[默认配置](examples/pipelines/data_configs)生成对应的测试与训练数据。若有自定义配置等需求可参考[Pipeline Usage](examples/pipelines/README_zh.md)进行个性化配置。
```bash
source examples/pipelines/run_pipeline.sh
```
生成的数据保存于[bootcamp_generator_outputs目录](examples/bootcamp_generator_outputs)，数据批次以时间戳命名，具体目录结构如下
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

## 模型训练
我们提供了两种训练框架（Xpuyu,Verl）的支持体系。
### Xpuyu
可参考[Xpuyu说明文档](examples/xpuyu_usage/README_zh.md)快速进行高效训练。
### Verl
要在Verl框架下加入Bootcamp任务进行训练，需要参考说明文档将bootcamp奖励计算方法嵌入verl框架，具体参考[Verl说明文档](examples/verl_usage/README_zh.md)进行。

## 模型评测
我们针对bootcamp任务，提供了个性化的评测服务，在使用FastChat、Ollama等框架部署好待测模型并获取对应API Url 与API Key后,使用如下命令可快速评测已部署的模型在**InternBootcamp_eval**评测集上的性能：
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
注意当api_mode指定为completion时，需正确设置对应的template（支持r1、qwen、internthinker、chatml（with no system prompt））。更详细的内容参考[评测手册](examples/unittests/README_zh.md)。