import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
import re




class CluckydaysInstructionGenerator(BaseInstructionGenerator):
    """Cluckydays Bootcamp指令生成器"""
    
    def __init__(self, max_period=1000, **params):
        """
        初始化Cluckydays指令生成器
        
        Args:
            max_period: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_period = max_period
        self.params = params
    
    def case_generator(self):
        a_params = self._generate_single_params()
        b_params = self._generate_single_params()
        return {
            'a_params': a_params,
            'b_params': b_params
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a_la, a_ra, a_ta = question_case['a_params']
        b_lb, b_rb, b_tb = question_case['b_params']
        problem = f"""Alice和Bob在竞赛中发现他们的幸运日存在周期性规律。请你帮助他们找出最长的连续共同幸运天数。

Alice的幸运日周期：
- 周期长度：{a_ta}天
- 每个周期的幸运日为第{a_la}天到第{a_ra}天（包含两端）
- 例如，第0个周期的幸运日是{a_la}~{a_ra}天，第1个周期为{a_ta+a_la}~{a_ta+a_ra}天，依此类推。

Bob的幸运日周期：
- 周期长度：{b_tb}天
- 每个周期的幸运日为第{b_lb}天到第{b_rb}天（包含两端）

任务：
找出两人共同的连续幸运日的最大天数。如果不存在重叠，则答案为0。

输入格式：
第一行三个整数：{a_la} {a_ra} {a_ta}
第二行三个整数：{b_lb} {b_rb} {b_tb}

请将最终答案以整数形式严格放置在[answer]和[/answer]之间，例如：[answer]5[/answer]。"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_single_params(self):
        ta = random.randint(2, self.max_period)
        max_s = ta - 1
        s = random.randint(1, max_s)
        la = random.randint(0, ta - s)
        ra = la + s - 1
        return [la, ra, ta]
