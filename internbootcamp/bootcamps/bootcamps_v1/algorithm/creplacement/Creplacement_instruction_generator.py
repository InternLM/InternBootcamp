import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CreplacementInstructionGenerator(BaseInstructionGenerator):
    """Creplacement Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Creplacement指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(5, 10))
        self.m = params.get('m', random.randint(3, 5))
    
    def case_generator(self):
        n, m = self.n, self.m
        s = [
            '.' if random.random() < 0.3 else random.choice('abcdefghijklmnopqrstuvwxyz')
            for _ in range(n)
        ]
        initial_str = ''.join(s)
        current_s = list(s)
        
        # Calculate initial score
        score = 0
        start = None
        last_char = None
        for i, c in enumerate(current_s):
            if last_char == '.' and c != '.':
                score += (i - start - 1)
                start = None
            if last_char != '.' and c == '.':
                start = i
            last_char = c
        if start is not None:
            score += (n - start - 1)
        
        # Generate queries and compute expected outputs
        queries = []
        expected_output = []
        for _ in range(m):
            xi = random.randint(1, n)
            ci = random.choice(['.', random.choice('abcdefghijklmnopqrstuvwxyz')])
            queries.append((xi, ci))
            
            # Update score based on query
            i = xi - 1
            original = current_s[i]
            new_char = ci
            if original == '.' and new_char != '.':
                if i > 0 and current_s[i-1] == '.':
                    score -= 1
                if i < n-1 and current_s[i+1] == '.':
                    score -= 1
            elif original != '.' and new_char == '.':
                if i > 0 and current_s[i-1] == '.':
                    score += 1
                if i < n-1 and current_s[i+1] == '.':
                    score += 1
            current_s[i] = new_char
            expected_output.append(score)
        
        return {
            'n': n,
            'm': m,
            'initial_string': initial_str,
            'queries': queries,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(case):
        prompt = [
            "Daniel has a string composed of lowercase letters and periods ('.').",
            "The minimum number of replacements needed to eliminate all consecutive '..' is denoted as f(s).",
            "Each query changes a character in the string, and you must compute f(s) after each change.",
            "\nProblem Instance:",
            f"Initial string: {case['initial_string']}",
            f"String length (n): {case['n']}, Number of queries (m): {case['m']}",
            "Queries (position and new character):"
        ]
        for idx, (pos, char) in enumerate(case['queries'], 1):
            prompt.append(f"{pos} {char}")
        prompt.append(
            "\nOutput the m results as space-separated integers. Place your answer within [answer] and [/answer], e.g., [answer]1 2 3[/answer]."
        )
        return '\n'.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

