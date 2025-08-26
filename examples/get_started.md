# Quick Start

InternBootcamp provides functionalities such as data generation, model training, model evaluation, and custom Bootcamp creation. Please refer to the following guide for a quick start.

To ensure the successful execution of subsequent operations, make sure you have installed InternBootcamp and set the project root directory as your working directory.

## Data Generation

Running [**run_pipeline.sh**](/examples/pipelines/run_pipeline.sh) will generate corresponding test and training data based on the **default configuration**`examples/pipelines/data_configs`. If you have custom configuration needs, please refer to [Pipeline Usage](pipelines/README.md) for personalized configuration.

```bash
source examples/pipelines/run_pipeline.sh
```

The generated data is saved in the **bootcamp_generator_outputs directory**`examples/bootcamp_generator_outputs`, with data batches named using timestamps. The specific directory structure is as follows:

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

## Model Training

We provide support systems for two training frameworks (Xpuyu and Verl).

### Xpuyu

Refer to the [Xpuyu documentation](/examples/xpuyu_usage/README.md) for efficient training.

### Verl

To incorporate Bootcamp tasks into training within the Verl framework, you need to embed the Bootcamp reward calculation method into the Verl framework according to the instructions. For details, see the [Verl documentation](/examples/verl_usage/README.md).

## Model Evaluation

We offer personalized evaluation services for Bootcamp tasks. After deploying the model to be tested using frameworks like FastChat or Ollama and obtaining the corresponding API URL and API Key, use the following command to quickly evaluate the performance of the deployed model on the **InternBootcamp_eval** dataset:

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
    --max_retrying_delay 60 \
    --resume
```

Note: When `api_mode` is set to `completion`, ensure that the corresponding `template` is correctly configured (supported options include `r1`, `qwen`, `internthinker`, and `chatml` (no system prompt)). For more details, refer to the [Evaluation Manual](/examples/unittests/README.md).

## Custom Bootcamp

If you need to create a custom Bootcamp task, follow these steps:

### 1. Create a new subdirectory under the `internbootcamp/bootcamp` directory, named after the Bootcamp task name

In this directory, you can define multiple versions of the task class. Below is an example using `binary_arithmetic_operations_default.py` (implementing a binary arithmetic operation Bootcamp) to demonstrate the entire process of creating a custom Bootcamp.

### 2. Create a Bootcamp class, inherit from the `Basebootcamp` class, and implement the `__init__` method

- The class name must end with `bootcamp`.
- Avoid defining mutable variables like `list` in the `__init__` method (recommended to define them in the `case_generator` method) to prevent non-reset variables from being reused.
- Avoid fixing random variables here (recommended to determine random variables in the `case_generator` method) to avoid generating repetitive data due to lack of randomness.
- Input parameters for the `__init__` method are configured via JSON files located in **examples/pipelines/puzzle_configs**, ensuring the JSON configuration file name matches the Bootcamp class name, e.g., `BinaryArithmeticOperationsbootcamp_test.json`, `BinaryArithmeticOperationsbootcamp_train.json`.

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

### 3. Implement the `case_generator` method (optional if no data generation is needed)

`case_generator` is an instance method used to generate parameters required to construct a single question or validate a response (i.e., parameters that uniquely determine a question), returning a parameter dictionary.

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

### 4. Implement the `prompt_func` method (optional if no data generation is needed)

`prompt_func` is an instance, static, or class method used to construct the problem statement for a single question, taking the parameter dictionary returned by `case_generator` as input `identity`, and returning the problem statement as a string.

```python
def prompt_func(self, identity: dict) -> str:
    return f"{identity['operand1']} {identity['operator']} {identity['operand2']} = ? Results should be rounded to {identity['precision']} decimal places and enclosed in double brackets like [[result]]."
```

### 5. Implement the `extract_output` method to extract answers from the model output

`extract_output` is a static method that accepts the model output as input `output` and returns the answer in any form.

```python
import re

@staticmethod
def extract_output(output):
    matches = re.findall(r'\[\[([^\[\]]+)\]\]', output)
    return matches[-1].strip() if matches else None
```

### 6. Implement the `_verify_correction` method to validate whether the model-generated answer is correct

`_verify_correction` is a class method that accepts the model output and the output of `case_generator` as input parameters `solution` and `identity`, returning a boolean indicating whether the answer is correct or a float/integer between 0 and 1 indicating the degree of correctness.

```python
@classmethod
def _verify_correction(cls, solution, identity: dict) -> bool:
    try:
        # Convert the string-form answer to a float
        solution = float(solution)
    except (ValueError, TypeError):
        return False

    # Calculate the correct answer based on the problem parameters
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
        # Check for division by zero
        if operand2 == 0:
            return False
        correct_answer = operand1 / operand2
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    # Round the correct answer to the specified precision
    correct_answer = round(correct_answer, precision)

    # Compare the model output with the correct answer
    return abs(solution - correct_answer) < 1e-6
```

### 7. Configure the JSON file (optional if no data generation is needed)

Create two JSON configuration files (for training and testing) in the `examples/pipelines/puzzle_configs` directory, with names matching the Bootcamp class name but without the "bootcamp" suffix (e.g., `BinaryArithmeticOperations_train.json`, `BinaryArithmeticOperations_test.json`), to define the parameters for this task. Below is an example configuration:

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

Ensure that the keys in the JSON file match the parameter names in the `__init__` method.

### 8. Register the custom Bootcamp task

To enable the system to recognize and load the custom Bootcamp task, register the task in `internbootcamp/bootcamp/__init__.py`. For example:

```python
from .binary_arithmetic_operations.binary_arithmetic_operations_default import BinaryArithmeticOperationsbootcamp
```

### 9. Test the custom Bootcamp task

After completing the above steps, you can test the custom Bootcamp task as follows:
1. Use `case_generator` to generate test cases.
2. Call `prompt_func` to generate the problem statement.
3. Use `extract_output` to extract answers from the model output.
4. Call `_verify_correction` to verify the correctness of the answer.

Below is a simple test code example:

```python
if __name__ == "__main__":
    # Initialize the Bootcamp task
    bootcamp = BinaryArithmeticOperationsbootcamp(
        operands_range=(0, 10),
        precision=3,
        operators=['+', '-', '*', '/']
    )

    # Generate a test case
    case = bootcamp.case_generator()
    print("Generated Case:", case)

    # Construct the problem statement
    prompt = bootcamp.prompt_func(case)
    print("Prompt:", prompt)

    # Simulate model output
    answer = eval(f"{case['operand1']} {case['operator']} {case['operand2']}")
    model_output = f"[[{round(answer, 3)}]]"
    extracted_answer = bootcamp.extract_output(model_output)
    print("Extracted Answer:", extracted_answer)

    # Verify the answer
    is_correct = bootcamp._verify_correction(extracted_answer, case)
    print("Is Correct:", is_correct)
```

### 10. Integrate into Pipeline (optional if no data generation is needed)

To integrate the custom Bootcamp task into the data generation pipeline, simply add the corresponding task definition to the two configuration files in the `examples/pipelines/data_configs` directory. For example:

```json
{
    "bootcamp_name": "BinaryArithmeticOperations",
    "sample_number": 64,
    "config_file": "BinaryArithmeticOperations",
    "bootcamp_cls_name": "BinaryArithmeticOperationsbootcamp"
}
```

Where:
- `bootcamp_name` is the task name (i.e., the class name without the `bootcamp` suffix).
- `sample_number` is the number of samples to generate.
- `config_file` is the configuration file name.
- `bootcamp_cls_name` is the task class name.

Alternatively, run the script [quickgen_data_configs.py](/examples/pipelines/quickgen_data_configs.py), which automatically generates corresponding pipeline configurations for Bootcamps configured in `examples/pipelines/puzzle_configs` and saves them in `examples/pipelines/data_configs`.

**By following the above steps, you can successfully create, test, and integrate a custom Bootcamp task!**