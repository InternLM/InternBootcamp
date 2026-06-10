import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class ArcRewardCalculator(BaseRewardCalculator):
    """Arc奖励计算器"""
    
    @staticmethod
    def extract_output(output:str)->Grid:
        """
        Extract the output from the solution.
        """
        json_objects = re.findall(r'\[\s*\[\s*.*?\s*\]\s*\]', output, re.DOTALL)
        json_obj = None
        for item in reversed(json_objects):
            try:
                json_obj = json.loads(item)
                if isinstance(json_obj, list) and all(isinstance(i, list) for i in json_obj):
                    return list_to_tuple(json_obj)
            except json.JSONDecodeError:
                continue
        return list_to_tuple(json_obj)
    
    @classmethod
    def _verify_correction(cls, solution:Grid, identity: dict) -> bool:
        """
        Verify the correction of the solution.
        
        Ensure all parameters are 'Grid' type.
        """
        if "std_ans" in identity and type(identity["std_ans"]) == str and list_to_tuple(json.loads(identity["std_ans"])) == solution:
            # 如果提供了答案，直接比较答案
            return True
        if "std_ans" in identity and type(identity["std_ans"]) == list and list_to_tuple(identity["std_ans"]) == solution:
            return True
        input_grid, task_key = identity['input_grid'], identity['task_key']
        if type(input_grid) == str:
            input_grid = list_to_tuple(json.loads(input_grid))
        else:
            input_grid = list_to_tuple(input_grid)
        verifier = cls.verifiers_mapper[task_key]  # 使用类变量 verifiers
        std_ans = verifier(input_grid)
        return std_ans == solution
    
    # 其他额外方法

