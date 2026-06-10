import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CvasilythebearandsequenceInstructionGenerator(BaseInstructionGenerator):
    """Cvasilythebearandsequence Bootcamp指令生成器"""
    
    def __init__(self, min_v=1, max_v=30, max_k=5):
        """
        初始化Cvasilythebearandsequence指令生成器
        
        Args:
            min_v: 参数描述
            max_v: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_v = min_v
        self.max_v = max_v
        self.max_k = max_k
    
    def case_generator(self):
        v_max = random.randint(self.min_v, self.max_v)
        base = 1 << v_max  # 2^v_max

        # Generate optimal subset (S_numbers)
        s_numbers = []
        current = base
        s_numbers.append(current)
        remaining = self.max_k - 1  # Already added the first number
        
        # Generate up to max_k numbers in [base, 2*base-1] range
        while remaining > 0 and current < (base << 1) - 1:
            next_num = random.randint(current + 1, (base << 1) - 1)
            s_numbers.append(next_num)
            current = next_num
            remaining -= 1

        # Generate lower numbers (if base allows)
        lower_count = random.randint(0, self.max_k)
        lower_numbers = []
        if base > 1 and lower_count > 0:
            available = list(range(1, base))
            if available:
                lower_numbers = sorted(random.sample(available, k=min(lower_count, len(available))))
        
        # Combine and sort the array
        a = sorted(lower_numbers + s_numbers)
        if not a:  # Fallback if empty (impossible due to s_numbers)
            a = [base]
            s_numbers = [base]

        return {
            'n': len(a),
            'a': a,
            'v_max': v_max,
            'base': base,
            's_count': len(s_numbers)  # Optimal subset size
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = question_case['a']
        problem_text = f"""Vasily the bear has a sequence of strictly increasing positive integers. Your task is to select a subset of these numbers such that the beauty of the subset is maximized. The beauty is defined as the maximum non-negative integer v for which the bitwise AND of all selected numbers is divisible by 2^v. If no such v exists (i.e., the bitwise AND is zero), the beauty is -1. Among all possible subsets with maximum beauty, you must choose the one with the largest possible size k. If there are multiple such subsets, any is acceptable.

Input:
- The first line contains an integer n ({n} in this case).
- The second line contains {n} strictly increasing integers: {' '.join(map(str, a))}.

Your output should be two lines:
- The first line is the integer k.
- The second line contains the selected numbers in any order.

Please provide your answer within [answer] and [/answer] tags. For example:

[answer]
2
4 5
[/answer]"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

