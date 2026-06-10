import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from itertools import combinations




class CarraybeautyInstructionGenerator(BaseInstructionGenerator):
    """Carraybeauty Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, a_min=0, a_max=10**5):
        """
        初始化Carraybeauty指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k = random.randint(2, n)
        a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        a.sort()
        return {
            'n': n,
            'k': k,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        a = question_case['a']
        a_str = ' '.join(map(str, a))
        problem = f"""你需要解决以下谜题：

给定一个长度为{n}的数组，数组中的元素依次为{a_str}。同时给定一个整数k={k}。你的任务是计算所有长度为k的子序列的“美”之和，并将结果对998244353取模。

子序列的定义是通过删除原数组中的若干元素（可能不删除或全部删除）后得到的序列。注意，子序列中的元素必须保持其在原数组中的相对顺序。

一个数组的“美”定义为该数组中任意两个元素之间的最小绝对差。例如，数组[1, 3, 5]的“美”是2，因为3-1=2，5-3=2，而5-1=4，取最小值为2。

你的答案是所有长度为k的子序列的“美”的总和模998244353的值。请确保你的答案放在[answer]标签中，例如[answer]42[/answer]。"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

