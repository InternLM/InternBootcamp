import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DdirtydeedsdonedirtcheapInstructionGenerator(BaseInstructionGenerator):
    """Ddirtydeedsdonedirtcheap Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Ddirtydeedsdonedirtcheap指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        n = self.n
        numbers = list(range(1, 2 * n + 1))
        random.shuffle(numbers)
        pairs = []
        for i in range(n):
            a = numbers[2 * i]
            b = numbers[2 * i + 1]
            if random.choice([True, False]):
                a, b = b, a
            pairs.append((a, b))
        return {
            'n': n,
            'pairs': pairs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        pairs = question_case['pairs']
        n = question_case['n']
        pairs_list = "\n".join([f"{a} {b}" for a, b in pairs])
        prompt = f"""You are given {n} pairs of integers. All integers in the pairs are distinct and each integer is between 1 and {2*n} inclusive. Your task is to select the largest subset of pairs and arrange them in order such that the resulting sequence alternates between increasing and decreasing (or vice versa).

For example, a valid sequence might look like 1 < 7 > 3 < 5 > 2 < 10 or 6 > 1 < 3 > 2 < 5 > 4. The goal is to include as many pairs as possible.

Input:
{n}
{pairs_list}

Your answer should be two lines. The first line contains the number of pairs selected, t. The second line contains t distinct indices (1-based) in the order they should be arranged. Please place your answer within [answer] and [/answer] tags.

Example:
[answer]
3
1 5 3
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def is_valid_sequence(seq):
        if len(seq) < 2 or len(seq) % 2 != 0:
            return False
        current_relation = seq[0] < seq[1]
        for i in range(1, len(seq)-1):
            next_relation = seq[i] < seq[i+1]
            if next_relation == current_relation:
                return False
            current_relation = next_relation
        return True
