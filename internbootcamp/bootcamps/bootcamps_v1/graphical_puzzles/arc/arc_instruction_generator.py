import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import sys
import re
import json
from pathlib import Path
from typing import Tuple
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.arc.lib.re_arc.main import get_generators
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.arc.lib.re_arc.main import get_verifiers

# === 源文件中的全局变量 ===

Grid = Tuple[Tuple[int]]

template = """
### **ARC Puzzle Simple Question Template**

1. **Problem Description**  
   - There is a logical relationship between the input and output grids. The goal is to deduce the rule and solve the test grid.

2. **Example Explanation**  
{examples}

3. **Test Grid**  
   **Input**:
```arcmatrix
[
{test_input}
]
```
**Output**:  
?
"""

example_template = """
- Example {index}:  
  **Input**:  
```arcmatrix
[
{input}
]
```  
  **Output**:  
```arcmatrix
[
{output}
]
```
"""



# === 源文件中的全局函数 ===

def list_to_tuple(l: list) -> Tuple:
    """递归地将列表转换为元组"""
    return tuple(list_to_tuple(item) if isinstance(item, list) else item for item in l)

def tuple_to_list(t: Tuple) -> list:
    """递归地将元组转换为列表"""
    return [tuple_to_list(item) if isinstance(item, tuple) else item for item in t]

def generate_arc_puzzle(examples, test_case):
    """
    Generates an ARC puzzle question.
    
    :param examples: List of dicts, each containing "input" and "output" fields.
    :param test_case: Dict containing "input" (grid for the test case).
    :return: Formatted puzzle string.
    """
    # Generate the examples section dynamically
    examples_section = ""
    for i, example in enumerate(examples, start=1):
        examples_section += example_template.format(
            index=i,
            input=',\n'.join([str(list(x)) for x in example["input"]]),
            output=',\n'.join([str(list(x)) for x in example["output"]])
        )
    
    # Format the full template
    return template.format(
        examples=examples_section.strip(),
        test_input=',\n'.join([str(list(x)) for x in test_case])
    )


class ArcInstructionGenerator(BaseInstructionGenerator):
    """Arc Bootcamp指令生成器"""
    
    def __init__(self, task_key_file: str = None, hint_examples_num: int = 3):
        """
        初始化Arc指令生成器
        
        Args:
            task_key_file: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        task_key_file = "/".join(__file__.split('/')[:-4]) + "/" + task_key_file
        self.task_keys = [json.loads(f) for f in open(task_key_file, 'r').readlines()]
        self.generators = get_generators()
        self.current_example = None
        self.hint_examples_num = hint_examples_num
    def case_generator(self):
        task_key = random.choice(self.task_keys)['key']
        if task_key not in self.generators:
            raise ValueError(f"Task key '{task_key}' not found in generators.")
        generator = self.generators[task_key]
        self.current_example = generator(0, 1)
        hint_examples = []
        for _ in range(self.hint_examples_num):
            hint_examples.append(generator(0, 1))

        input_grid = self.current_example['input']
        return  {'hint_examples':hint_examples ,'input_grid': input_grid, 'task_key': task_key}
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        """
        return generate_arc_puzzle(identity['hint_examples'], identity['input_grid']) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

