# 快速开始

InternBootcamp 提供了数据生成、模型训练、模型评测和自定义 Bootcamp 等功能。请参考以下指南快速入门。

为确保后续操作成功执行，请确保您已经安装了 InternBootcamp，并将项目根目录设为工作目录。

## 数据生成

运行 [**run_pipeline.sh**](/examples/pipelines/run_pipeline.sh) 即可根据 **默认配置**`examples/pipelines/data_configs`生成对应的测试与训练数据。若有自定义配置需求，请参考 [Pipeline Usage](pipelines/README_zh.md) 进行个性化配置。

```bash
source examples/pipelines/run_pipeline.sh
```

生成的数据保存于 **bootcamp_generator_outputs 目录**`examples/bootcamp_generator_outputs`，数据批次以时间戳命名，具体目录结构如下：

```
examples/
├── ...
└── bootcamp_generator_outputs/
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

我们提供了两种训练框架（Xpuyu 和 Verl）的支持体系。

### Xpuyu

可参考 [Xpuyu 说明文档](/examples/xpuyu_usage/README_zh.md) 快速进行高效训练。

### Verl

要在 Verl 框架下加入 Bootcamp 任务进行训练，需要参考说明文档将 Bootcamp 奖励计算方法嵌入 Verl 框架，具体参考 [Verl 说明文档](/examples/verl_usage/README_zh.md)。

## 模型评测

我们针对 Bootcamp 任务提供了个性化的评测服务。在使用 FastChat、Ollama 等框架部署好待测模型并获取对应的 API URL 和 API Key 后，使用以下命令可快速评测已部署的模型在 **InternBootcamp_eval** 评测集上的性能：

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

注意：当 `api_mode` 指定为 `completion` 时，需正确设置对应的 `template`（支持 `r1`、`qwen`、`internthinker`、`chatml`（无系统提示））。更详细的内容请参考 [评测手册](/examples/unittests/README_zh.md)。

## 自定义 Bootcamp

若需新建自定义 Bootcamp 任务，可参考以下流程：

### 1. 在目录 `internbootcamp/bootcamp` 下新建一个子目录，命名为 Bootcamp 任务名称

在该目录下可定义该任务类的多个版本。以下将以 `binary_arithmetic_operations_default.py` 为例（实现一个二项四则运算 Bootcamp），展示新建自定义 Bootcamp 的全流程。

### 2. 创建一个 Bootcamp 类，继承 `Basebootcamp` 类，并实现 `__init__` 方法

- 类名必须以 `bootcamp` 为后缀。
- 谨慎将类似 `list` 的可变变量定义在 `__init__` 方法中（推荐在 `case_generator` 方法里定义），避免导致未重置的变量被重复使用。
- 谨慎将有随机性的变量在此处确定（推荐在 `case_generator` 方法里确定随机变量），避免生成数据时缺少随机性导致数据重复。
- `__init__` 方法的输入参数将以 JSON 文件形式配置于 **examples/pipelines/puzzle_configs**，确保 JSON 配置文件命名与 Bootcamp 类名一致，例如 `BinaryArithmeticOperationsbootcamp_test.json`、`BinaryArithmeticOperationsbootcamp_train.json`。

```python
from internbootcamp.bootcamp.base import Basebootcamp

class BinaryArithmeticOperationsbootcamp(Basebootcamp):
    def __init__(self, operands_range=(0, 10), precision=3, operators=['+', '-', '*', '/']):
        self.operands_range = operands_range
        self.precision = precision
        self.operators = operators

    def case_generator(self):
        pass

    def prompt_func(self, identity) -> dict:
        pass

    @staticmethod
    def extract_output(output):
        pass

    @classmethod
    def _verify_correction(cls, solution, identity: dict):
        pass
```

### 3. 实现 `case_generator` 方法（可选，若无需生成数据，则不需要实现）

`case_generator` 为实例方法，用于生成构造单个题目或验证一次回答所需的参数（即可以唯一确定一个题目所需的参数），并返回参数字典。

```python
import random

def case_generator(self) -> dict:
    operand1 = round(random.uniform(*self.operands_range), self.precision)
    operand2 = round(random.uniform(*self.operands_range), self.precision)
    operator = random.choice(self.operators)
    while operator == '/' and operand2 == 0:
        operand2 = round(random.uniform(*self.operands_range), self.precision)
    case = {}
    case['operand1'] = operand1
    case['operand2'] = operand2
    case['operator'] = operator
    case['precision'] = self.precision
    return case
```

### 4. 实现 `prompt_func` 方法（可选，若无需生成数据，则不需要实现）

`prompt_func` 为实例、静态或类方法，用于构造单个题目的题面，接受 `case_generator` 返回的参数字典作为输入参数 `identity`，并以字符串形式返回题面。

```python
def prompt_func(self, identity: dict) -> str:
    return f"{identity['operand1']} {identity['operator']} {identity['operand2']} = ? 结果请保留小数点后{identity['precision']}位，并以[[]]包裹你的答案，如[[result]]。"
```

### 5. 实现 `extract_output` 方法，用于提取模型输出的答案

`extract_output` 为静态方法，接受模型输出作为输入参数 `output`，并以任意形式返回答案。

```python
import re

@staticmethod
def extract_output(output):
    matches = re.findall(r'\[\[([^\[\]]+)\]\]', output)
    return matches[-1].strip() if matches else None
```

### 6. 实现 `_verify_correction` 方法，用于验证模型生成的答案是否正确

`_verify_correction` 为类方法，接受模型输出和 `case_generator` 的输出作为输入参数 `solution` 和 `identity`，返回一个布尔值表示答案是否正确，或返回 0 到 1 之间的一个浮点型或整数型数字表示答案的正确程度。

```python
@classmethod
def _verify_correction(cls, solution, identity: dict) -> bool:
    try:
        # 将字符串形式的答案转换为浮点数
        solution = float(solution)
    except (ValueError, TypeError):
        return False

    # 根据题目参数计算正确答案
    operand1 = identity['operand1']
    operand2 = identity['operand2']
    operator = identity['operator']
    precision = identity['precision']

    if operator == '+':
        correct_answer = operand1 + operand2
    elif operator == '-':
        correct_answer = operand1 - operand2
    elif operator == '*':
        correct_answer = operand1 * operand2
    elif operator == '/':
        # 检查除零错误
        if operand2 == 0:
            return False
        correct_answer = operand1 / operand2
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    # 对正确答案进行精度处理
    correct_answer = round(correct_answer, precision)

    # 比较模型输出与正确答案
    return abs(solution - correct_answer) < 1e-6
```

### 7. 配置 JSON 文件（可选，若无需生成数据，则不需要实现）

在 `examples/pipelines/puzzle_configs` 目录下创建一个与 Bootcamp 类名一致的 JSON 配置文件（如 `BinaryArithmeticOperationsbootcamp_train.json`），用于定义该任务的参数。以下是一个示例配置：

```json
[
    {
        "operands_range": [-10, 10],
        "precision": 3,
        "operators": ["+", "-", "*", "/"]
    },
    {
        "operands_range": [10, 1000],
        "precision": 4,
        "operators": ["+", "-", "*", "/"]
    }
]
```

确保 JSON 文件中的键与 `__init__` 方法的参数名称一致。

### 8. 注册自定义 Bootcamp 任务

为了使系统能够识别并加载自定义的 Bootcamp 任务，需要在 `internbootcamp/bootcamp/__init__.py` 中注册该任务。例如：

```python
from .binary_arithmetic_operations.binary_arithmetic_operations_default import BinaryArithmeticOperationsbootcamp
```

### 9. 测试自定义 Bootcamp 任务

在完成上述步骤后，可以通过以下方式测试自定义的 Bootcamp 任务：
1. 使用 `case_generator` 生成测试用例。
2. 调用 `prompt_func` 生成题面。
3. 使用 `extract_output` 提取模型输出的答案。
4. 调用 `_verify_correction` 验证答案的正确性。

以下是一个简单的测试代码示例：

```python
if __name__ == "__main__":
    # 初始化 Bootcamp 任务
    bootcamp = BinaryArithmeticOperationsbootcamp(
        operands_range=(0, 10),
        precision=3,
        operators=['+', '-', '*', '/']
    )

    # 生成测试用例
    case = bootcamp.case_generator()
    print("Generated Case:", case)

    # 构造题面
    prompt = bootcamp.prompt_func(case)
    print("Prompt:", prompt)

    # 模拟模型输出
    answer = eval(f"{case['operand1']} {case['operator']} {case['operand2']}")
    model_output = f"[[{round(answer, 3)}]]"
    extracted_answer = bootcamp.extract_output(model_output)
    print("Extracted Answer:", extracted_answer)

    # 验证答案
    is_correct = bootcamp._verify_correction(extracted_answer, case)
    print("Is Correct:", is_correct)
```

### 10. 集成到 Pipeline（可选，若无需生成数据，则不需要实现）

将自定义的 Bootcamp 任务集成到数据生成 Pipeline 中，只需要在 `examples/pipelines/data_configs` 目录下的两个配置文件中添加相应的任务定义。例如：

```json
{
    "bootcamp_name": "BinaryArithmeticOperations",
    "sample_number": 64,
    "config_file": "BinaryArithmeticOperations",
    "bootcamp_cls_name": "BinaryArithmeticOperationsbootcamp"
}
```

其中：
- `bootcamp_name` 为任务名称（即类名去除 `bootcamp` 后缀）。
- `sample_number` 为生成样本数量。
- `config_file` 为配置文件名。
- `bootcamp_cls_name` 为任务类名。

或运行脚本 [quickgen_data_configs.py](/examples/pipelines/quickgen_data_configs.py)，默认可自动将 `examples/pipelines/puzzle_configs` 下配置的 Bootcamp 生成对应的 Pipeline 配置并覆盖保存于 `examples/pipelines/data_configs`。

**通过以上步骤，您可以成功创建、测试并集成一个自定义的 Bootcamp 任务！**