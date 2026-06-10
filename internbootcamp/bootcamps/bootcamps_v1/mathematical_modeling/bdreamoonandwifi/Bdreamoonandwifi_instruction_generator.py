import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math




class BdreamoonandwifiInstructionGenerator(BaseInstructionGenerator):
    """Bdreamoonandwifi Bootcamp指令生成器"""
    
    def __init__(self, max_length=10, p_question=0.3):
        """
        初始化Bdreamoonandwifi指令生成器
        
        Args:
            max_length: 参数描述
            p_question: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()  # 显式调用父类初始化
        self.max_length = max_length
        self.p_question = p_question
    
    def case_generator(self):
        length = random.randint(1, self.max_length)
        s1 = ''.join(random.choices('+-', k=length))
        s2 = ''.join([
            '?' if random.random() < self.p_question else random.choice('+-') 
            for _ in range(length)
        ])
        return {
            's1': s1,
            's2': s2,
            '_target': self._calculate_probability(s1, s2)
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        return f"""Drazil的原始指令：{case['s1']}
接收到的含噪声指令：{case['s2']}
每个?表示随机选择±1。请计算最终位置一致的概率（12位小数格式在[answer]标签中）：
示例：[answer]0.123456789012[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_probability(cls, s1, s2):
        """ 精确的概率计算核心 """
        # 计算原始目标位置
        target_pos = sum(1 if c == '+' else -1 for c in s1)

        # 解析接收到的指令
        fixed_pos = 0
        unknown_count = 0
        for c in s2:
            if c == '+':
                fixed_pos += 1
            elif c == '-':
                fixed_pos -= 1
            else:
                unknown_count += 1

        # 计算需要补偿的位移
        required_offset = target_pos - fixed_pos

        # 检查是否可能满足
        if (required_offset + unknown_count) % 2 != 0:
            return 0.0
        if abs(required_offset) > unknown_count:
            return 0.0

        # 计算组合数
        k = (required_offset + unknown_count) // 2
        try:
            combinations = math.comb(unknown_count, k)
        except AttributeError:  # 兼容Python <3.10
            combinations = math.factorial(unknown_count) // (
                math.factorial(k) * math.factorial(unknown_count - k))

        return combinations / (2 ** unknown_count)
