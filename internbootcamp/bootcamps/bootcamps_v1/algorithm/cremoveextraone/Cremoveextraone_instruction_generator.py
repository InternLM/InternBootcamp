import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import bisect




class CremoveextraoneInstructionGenerator(BaseInstructionGenerator):
    """Cremoveextraone Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Cremoveextraone指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize permutation record puzzle bootcamp with parameters for permutation size.

        Args:
            min_n (int): Minimum length of permutation (inclusive)
            max_n (int): Maximum length of permutation (inclusive)
        """
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """
        Generate a permutation puzzle case with optimal removable element.
        
        Returns:
            dict: {'n', 'p', 'answer'} where p is permutation list, answer is optimal element
        """
        n = random.randint(self.min_n, self.max_n)
        p = list(range(1, n+1))
        random.shuffle(p)
        answer = self._compute_correct_answer(p)
        return {
            'n': n,
            'p': p,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        Format the puzzle case into an instructional prompt with answer format specification.
        """
        n = question_case['n']
        p_str = ' '.join(map(str, question_case['p']))
        return f"""You are participating in a programming competition. Solve the following problem:

**Problem Statement:**
Given a permutation p of length n, remove exactly one element to maximize the number of records in the remaining sequence. A record is an element that is larger than all preceding elements. If multiple elements yield the maximum records, choose the smallest one.

**Input Format:**
- First line: Integer n ({n} in this case)
- Second line: Space-separated permutation elements ({p_str})

**Output Format:**
A single integer - the element to remove. Place your answer between [answer] and [/answer] tags. 

**Example:**
For input:
5
5 1 2 3 4
The correct answer is [answer]5[/answer].

**Your Task:**
Apply the problem-solving process and output your final answer within the specified tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_correct_answer(p):
        """
        Compute correct answer using optimized approach from reference code.
        """
        n = len(p)
        nums_sorted = []
        record_prevented = [0] * (n + 2)  # +2 to avoid index issues

        for num in p:
            bisect.insort(nums_sorted, num)
            ind = nums_sorted.index(num)

            if ind == len(nums_sorted) - 1:
                record_prevented[num] = -1
            elif ind == len(nums_sorted) - 2:
                record_prevented[nums_sorted[-1]] += 1

            if len(nums_sorted) > 2:
                nums_sorted.pop(0)

        mx, mx_num = -1, float('inf')
        for num in range(1, n+1):
            if record_prevented[num] > mx or (record_prevented[num] == mx and num < mx_num):
                mx = record_prevented[num]
                mx_num = num

        return mx_num
