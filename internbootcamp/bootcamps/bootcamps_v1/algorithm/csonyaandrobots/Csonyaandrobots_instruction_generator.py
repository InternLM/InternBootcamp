import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import bisect
from collections import defaultdict




class CsonyaandrobotsInstructionGenerator(BaseInstructionGenerator):
    """Csonyaandrobots Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=1000, max_value=100000):
        """
        初始化Csonyaandrobots指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_value = max_value
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(1, self.max_value) for _ in range(n)]
        return {"n": n, "a": a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        prompt = f"""索尼娅在一行中放置了{n}个数字：{a_str}。她在行的两端各放置了一个机器人。左边的机器人被赋予数字p，右边的被赋予数字q。两个机器人开始相向移动：

- 左边机器人向右移动，在找到第一个p时停在对应位置
- 右边机器人向左移动，在找到第一个q时停在对应位置

有效条件：左边机器人位置必须严格小于右边机器人位置，且p和q必须存在于数组中。

请计算所有有效(p, q)对的数量。答案放入[answer][/answer]。例如，对于输入：
5
1 5 4 1 3

正确格式：[answer]9[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

