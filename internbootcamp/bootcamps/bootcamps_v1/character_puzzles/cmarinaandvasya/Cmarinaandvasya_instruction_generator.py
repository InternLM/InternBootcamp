import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CmarinaandvasyaInstructionGenerator(BaseInstructionGenerator):
    """Cmarinaandvasya Bootcamp指令生成器"""
    
    def __init__(self, max_n=10):
        """
        初始化Cmarinaandvasya指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
    
    def case_generator(self):
        # Decide case type: 70% solvable, 30% impossible
        if random.random() < 0.7:
            if random.choice([True, False]):
                # Case 1: Generate s3 first (two modified variants)
                n = random.randint(1, self.max_n)
                t = random.randint(0, n)
                s3 = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n)])
                
                s1 = list(s3)
                indices = random.sample(range(n), t)
                for i in indices:
                    available = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c != s1[i]]
                    s1[i] = random.choice(available)
                s1 = ''.join(s1)
                
                s2 = list(s3)
                indices = random.sample(range(n), t)
                for i in indices:
                    available = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c != s2[i]]
                    s2[i] = random.choice(available)
                s2 = ''.join(s2)
                
                return {
                    'n': n, 't': t, 's1': s1, 's2': s2, 'possible': True
                }
            else:
                # Case 2: Generate identical s1/s2 with valid solution
                n = random.randint(1, self.max_n)
                t = random.randint(0, n)
                s1 = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n)])
                s2 = s1
                return {
                    'n': n, 't': t, 's1': s1, 's2': s2, 'possible': True
                }
        else:
            if random.random() < 0.5:
                # Classic impossible case: n=1, t=0, different strings
                return {
                    'n': 1, 't': 0, 's1': 'a', 's2': 'b', 'possible': False
                }
            else:
                # Generate case with t < minimal required t
                n = random.randint(2, self.max_n)
                d = random.randint(1, n)
                s1 = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n)])
                s2 = list(s1)
                # Create d differences
                indices = random.sample(range(n), d)
                for i in indices:
                    available = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c != s2[i]]
                    s2[i] = random.choice(available)
                s2 = ''.join(s2)
                # Calculate minimal required t
                t_min = (d + 1) // 2
                t = max(0, t_min - 1)
                return {
                    'n': n, 't': t, 's1': s1, 's2': s2, 'possible': False
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        t = question_case['t']
        s1 = question_case['s1']
        s2 = question_case['s2']
        prompt = f"""Given two strings of length {n}, find a third string differing from both in exactly {t} positions.
        
Input:
{n} {t}
{s1}
{s2}

Rules:
1. Output must be length {n} and use lowercase letters
2. If impossible, output -1
3. Format answer within [answer][/answer] tags

Example valid response:
[answer]axyz[/answer] or [answer]-1[/answer]

Now solve this:"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

