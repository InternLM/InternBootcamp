import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CrotationmatchingInstructionGenerator(BaseInstructionGenerator):
    """Crotationmatching Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=10, rotation_prob=0.5):
        """
        初始化Crotationmatching指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            rotation_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.rotation_prob = rotation_prob
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        a = list(range(1, n + 1))
        random.shuffle(a)
        
        if random.random() < self.rotation_prob:
            shift = random.randint(0, n - 1)
            b = a[shift:] + a[:shift]
        else:
            if random.random() < 0.5:
                b = a[::-1]
            else:
                b = list(range(1, n + 1))
                random.shuffle(b)
        
        return {
            'n': n,
            'a': a,
            'b': b
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        b_str = ' '.join(map(str, question_case['b']))
        return f"""You are a puzzle solver. Help Ishika and Hriday find the maximum number of matching pairs after performing any number of cyclic shifts on either permutation. 

**Problem Description:**
After the mysterious disappearance of Ashish, his two disciples were left with permutations a and b. They can cyclically shift their respective permutations any number of times. A matching pair occurs when elements at the same index are equal. Your task is to determine the maximum possible number of such pairs.

**Operations Allowed:**
- Cyclic left shift: Each element moves to the previous index, and the first element wraps to the end.
- Cyclic right shift: Each element moves to the next index, and the last element wraps to the start.

**Input Format:**
- The first line contains an integer n (1 ≤ n ≤ 2×10^5), the size of the permutations.
- The second line contains permutation a.
- The third line contains permutation b.

**Output Format:**
A single integer indicating the maximum number of matching pairs.

**Example Input:**
5
1 2 3 4 5
2 3 4 5 1

**Example Output:**
5

**Your Task:**
n: {n}
a: {a_str}
b: {b_str}

Please provide your answer as a single integer enclosed within [answer] and [/answer] tags. For example: [answer]5[/answer]. Ensure your final answer is the last one provided.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

