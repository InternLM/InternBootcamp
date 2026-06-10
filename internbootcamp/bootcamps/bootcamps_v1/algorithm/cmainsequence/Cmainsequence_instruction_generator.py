import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CmainsequenceInstructionGenerator(BaseInstructionGenerator):
    """Cmainsequence Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, **kwargs):
        """
        初始化Cmainsequence指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
    
    def case_generator(self):
        # 50% chance to generate valid/invalid cases
        if random.choice([True, False]):
            return self._generate_valid_case()
        else:
            return self._generate_invalid_case()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Help Vova recover the correct bracket sequence from:
Input format:
1. First line: n = {question_case['n']}
2. Second line: {' '.join(map(str, question_case['p']))}
3. Third line: {question_case['t']} {' '.join(map(str, question_case['q'])) if question_case['t'] else ''}

Rules:
- Sequence must be valid bracket sequence
- Absolute values must match p sequence
- Negative positions must exactly match q list

Output format:
[answer]
YES/NO
sequence (if YES)
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_case(self):
        """Generate a valid case with proper bracket sequence"""
        n = random.randint(2, self.max_n // 2) * 2  # Even number
        while True:
            stack = []
            p_list = []
            x_list = []
            q_list = []

            # Generate elements in reverse order
            for i in reversed(range(n)):
                if stack:
                    v = stack.pop()
                    x_val = v
                else:
                    v = random.randint(1, 10**3)  # Reduced range for test cases
                    x_val = -v
                    q_list.append(i + 1)  # 1-based position
                    stack.append(v)
                p_list.append(abs(x_val))
                x_list.append(x_val)

            # Reverse to get correct order
            p = p_list[::-1]
            x = x_list[::-1]
            q = sorted(q_list)

            if self._validate_x(x):
                return {
                    'n': n,
                    'p': p,
                    't': len(q),
                    'q': q
                }

    def _generate_invalid_case(self):
        """Generate invalid case with impossible solution"""
        # Case type 1: Odd length
        if random.choice([True, False]):
            n = random.choice([x for x in range(1, self.max_n+1) if x % 2 != 0])
            p = [random.randint(1, 10**3) for _ in range(n)]
            t = random.randint(0, n)
            q = random.sample(range(1, n+1), t)
        # Case type 2: Valid length but wrong q positions
        else:
            n = random.randint(2, self.max_n // 2) * 2
            p = [random.randint(1, 10**3) for _ in range(n)]
            t = random.randint(0, n)
            q = random.sample(range(1, n+1), t)
            # Ensure at least one q position is invalid
            if q and random.choice([True, False]):
                q[0] = (q[0] % n) + 1  # Modify first position

        return {
            'n': n,
            'p': p,
            't': len(q),
            'q': sorted(q)
        }

    @staticmethod
    def _validate_x(x):
        """Validate generated bracket sequence"""
        stack = []
        for num in x:
            if num > 0:
                stack.append(num)
            else:
                if not stack or stack[-1] != -num:
                    return False
                stack.pop()
        return not stack
