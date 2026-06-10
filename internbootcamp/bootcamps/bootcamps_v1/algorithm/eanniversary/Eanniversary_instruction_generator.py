import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EanniversaryInstructionGenerator(BaseInstructionGenerator):
    """Eanniversary Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Eanniversary指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        pass
    
    def case_generator(self):
        m = random.randint(1, 10**9)
        l = random.randint(1, 10**12)
        r = random.randint(l + 1, 10**12)
        k = random.randint(2, r - l + 1)
        return {
            'm': m,
            'l': l,
            'r': r,
            'k': k
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        l = question_case['l']
        r = question_case['r']
        k = question_case['k']
        prompt = (
            f"给定四个整数 m = {m}, l = {l}, r = {r}, k = {k}。\n"
            "你需要解决的问题是：找到区间 [l, r] 中所有 k 个元素的子集，"
            "计算每个子集对应斐波那契数索引的最大公约数，然后找出这些公约数中的最大值。"
            "将这个最大公约数代入斐波那契数列中，计算其模 m 的值。\n"
            "斐波那契数列定义为：F1 = 1, F2 = 1, Fn = Fn-1 + Fn-2，n ≥ 3。\n"
            "请将答案以整数形式放在 [answer] 标签内。例如，如果计算结果是 3，"
            "那么回答应为：[answer]3[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

