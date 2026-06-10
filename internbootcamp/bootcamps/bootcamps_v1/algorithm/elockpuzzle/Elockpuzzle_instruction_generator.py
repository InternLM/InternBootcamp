import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string




class ElockpuzzleInstructionGenerator(BaseInstructionGenerator):
    """Elockpuzzle Bootcamp指令生成器"""
    
    def __init__(self, n=6, allow_unsolvable=True):
        """
        初始化Elockpuzzle指令生成器
        
        Args:
            n: 参数描述
            allow_unsolvable: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.allow_unsolvable = allow_unsolvable
    
    def case_generator(self):
        # Randomly decide to generate solvable or unsolvable case
        generate_unsolvable = self.allow_unsolvable and random.choice([False, True])
        
        if generate_unsolvable:
            # Generate s and t with different character frequencies
            while True:
                s = ''.join(random.choices(string.ascii_lowercase, k=self.n))
                t = ''.join(random.choices(string.ascii_lowercase, k=self.n))
                if sorted(s) != sorted(t):
                    break
            return {'n': self.n, 's': s, 't': t}
        else:
            # Generate solvable case by applying random shifts
            s = ''.join(random.choices(string.ascii_lowercase, k=self.n))
            current = s
            k = random.randint(0, min(100, 6100))  # Generate up to 100 shifts
            for _ in range(k):
                x = random.randint(0, self.n)
                current = self._apply_shift(current, x, self.n)
            return {'n': self.n, 's': s, 't': current}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        s = question_case['s']
        t = question_case['t']
        prompt = f"""You are an explorer trying to crack a code lock. The lock displays a string of {n} lowercase letters. Initially, it shows "{s}". Your goal is to transform it into "{t}" using "shift x" operations. Each operation chooses x (0 ≤ x ≤ {n}), reverses the last x characters, and moves them to the front.

For example, applying shift 4 to "abcacb" results in "bcacab" (split into "ab" + "cacb", reversed to "bcac" + "ab").

Your task is to find a sequence of up to 6100 shifts to achieve this transformation. If impossible, output -1.

Format your answer within [answer] tags:
- If possible: first line is k (number of operations), second line is x1 x2 ... xk.
- If impossible: single line -1.

Example:
[answer]
4
6 3 2 3
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _apply_shift(cls, s, x, n):
        if x < 0 or x > n or len(s) != n:
            return None
        if x == 0:
            return s
        return s[-x:][::-1] + s[:-x]
