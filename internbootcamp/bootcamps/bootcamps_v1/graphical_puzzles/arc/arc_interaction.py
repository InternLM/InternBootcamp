from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class ArcInteraction(BaseInteraction):
    """Arc交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = ArcRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个arc问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法

