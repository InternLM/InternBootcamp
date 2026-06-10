import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ElittleelephantandshiftsInstructionGenerator(BaseInstructionGenerator):
    """Elittleelephantandshifts Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Elittleelephantandshifts指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize the Elittleelephantandshiftsbootcamp with parameters.
        Parameters:
            params (dict): Contains puzzle parameters, e.g., 'n' for permutation size.
        """
        super().__init__()  # Corrected: No parameters passed to super()
        self.n = params.get('n', 4)
    
    def case_generator(self):
        """
        Generates a problem instance with random permutations a and b, and precomputes the correct answers.
        Returns a JSON-serializable dictionary containing the instance data.
        """
        n = self.n
        a = list(range(1, n + 1))
        random.shuffle(a)
        b = list(range(1, n + 1))
        random.shuffle(b)

        # Precompute positions for each element in a and b (0-based)
        inda = {num-1: idx for idx, num in enumerate(a)}
        indb = {num-1: idx for idx, num in enumerate(b)}

        # Compute the correct output for each cyclic shift
        correct_outputs = []
        for k in range(n):
            min_distance = min(
                abs((indb[x] - k) % n - inda[x])
                for x in range(n)
            )
            correct_outputs.append(min_distance)

        return {
            'n': n,
            'a': a,
            'b': b,
            'correct_outputs': correct_outputs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        Converts the generated problem instance into a formatted question string.
        """
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        b_str = ' '.join(map(str, question_case['b']))
        prompt = f"""You are a programming assistant. Solve the following puzzle:

Given two permutations a and b of length {n}, compute the distance between permutation a and each cyclic shift of permutation b. The distance is defined as the minimum absolute difference between the positions of the same number in a and the shifted b. 

Input format:
- First line: integer n
- Second line: permutation a (space-separated integers)
- Third line: permutation b (space-separated integers)

Output format:
Output {n} lines, each containing the distance for the corresponding cyclic shift of b. The shifts are numbered from 1 to n.

Example:
If n=2, a is 1 2, and b is 2 1, the correct output is:
1
0

Now, solve the following problem:
Input:
{n}
{a_str}
{b_str}

Write your answer as exactly {n} integers, each on a new line, enclosed within [answer] and [/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

