import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.arc.arc_reward_calculator import ArcRewardCalculator

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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ArcVerificationTool(BaseTool):
    """Arc验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = ArcRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"ArcVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

