import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CbuildingpermutationInstructionGenerator(BaseInstructionGenerator):
    """Cbuildingpermutation Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cbuildingpermutation指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 2)
        self.max_n = params.get('max_n', 10)
        self.value_range = params.get('value_range', (-10, 10))
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        permutation = list(range(1, n+1))
        a = [x + random.randint(*self.value_range) for x in permutation]
        random.shuffle(a)
        return {
            'n': n,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        prompt = (
            f"你有一个整数序列：{a}。你的任务是计算将其转换为一个排列所需的最小移动次数。排列是指包含1到{n}每个数恰好一次的序列。"
            f"移动是指将一个数增加或减少1的次数。例如，将3变成2需要1次移动。"
            f"请计算将该序列转换为排列所需的最小总移动次数，并将你的答案放在[answer]标签中。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

