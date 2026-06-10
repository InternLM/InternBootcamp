import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DfibonacciishInstructionGenerator(BaseInstructionGenerator):
    """Dfibonacciish Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=1000):
        """
        初始化Dfibonacciish指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数校验和范围限制
        """
        self.min_n = max(2, min_n)
        self.max_n = min(1000, max(max_n, self.min_n))
        if self.min_n > self.max_n:
            raise ValueError("Invalid range: min_n cannot be larger than max_n")
    
    def case_generator(self):
        """
        改进后的案例生成逻辑，确保生成有效案例
        """
        # 全零案例处理
        if random.random() < 0.2:  # 20%概率生成全零案例
            n = random.randint(self.min_n, self.max_n)
            return {
                'n': n,
                'arr': [0]*n,
                'expected': n
            }
        
        # 常规案例生成（确保所有元素可用于构建序列）
        for _ in range(100):  # 最大尝试次数
            # 生成非零初始值
            a, b = 0, 0
            while a == 0 and b == 0:
                a = random.randint(-10, 10)
                b = random.randint(-10, 10)
            
            # 构建合法序列
            seq = [a, b]
            while len(seq) < self.max_n:
                next_val = seq[-1] + seq[-2]
                if abs(next_val) > 1e9:
                    break
                seq.append(next_val)
            
            # 确保序列长度符合要求
            if self.min_n <= len(seq) <= self.max_n:
                shuffled = seq.copy()
                random.shuffle(shuffled)
                return {
                    'n': len(seq),
                    'arr': shuffled,
                    'expected': len(seq)
                }
        
        # 生成失败时返回最小有效案例
        return {
            'n': 2,
            'arr': [1, 1],
            'expected': 2
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """增强格式规范说明"""
        return f"""You are given a sequence of {question_case['n']} integers: {' '.join(map(str, question_case['arr']))}
        
Your task is to rearrange them to form the longest possible Fibonacci-ish sequence. The sequence must:
1. Contain at least 2 elements
2. Follow the rule: each element after the first two is the sum of the preceding two

Output ONLY the maximum length as:
[answer]length[/answer]

Example1:
Input: 3 1 2 -1 → [answer]3[/answer]

Your turn:""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

