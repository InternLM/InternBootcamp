import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CswaplettersInstructionGenerator(BaseInstructionGenerator):
    """Cswapletters Bootcamp指令生成器"""
    
    def __init__(self, n=4):
        """
        初始化Cswapletters指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        # Decide whether to generate an impossible case
        make_impossible = random.choice([True, False])
        
        s = list(''.join(random.choice(['a', 'b']) for _ in range(self.n)))
        t = list(''.join(random.choice(['a', 'b']) for _ in range(self.n)))
        
        current_total_a = ''.join(s).count('a') + ''.join(t).count('a')
        
        if make_impossible:
            # Ensure total_a is odd
            if current_total_a % 2 == 0:
                # Flip a character
                if random.choice([True, False]):
                    idx = random.randint(0, self.n-1)
                    s[idx] = 'a' if s[idx] == 'b' else 'b'
                else:
                    idx = random.randint(0, self.n-1)
                    t[idx] = 'a' if t[idx] == 'b' else 'b'
        else:
            # Ensure total_a is even
            if current_total_a % 2 != 0:
                # Flip a character to make even
                if random.choice([True, False]):
                    idx = random.randint(0, self.n-1)
                    s[idx] = 'a' if s[idx] == 'b' else 'b'
                else:
                    idx = random.randint(0, self.n-1)
                    t[idx] = 'a' if t[idx] == 'b' else 'b'
                # Check again and flip if still odd
                current_total_a = ''.join(s).count('a') + ''.join(t).count('a')
                if current_total_a % 2 != 0:
                    if random.choice([True, False]):
                        idx = random.randint(0, self.n-1)
                        s[idx] = 'a' if s[idx] == 'b' else 'b'
                    else:
                        idx = random.randint(0, self.n-1)
                        t[idx] = 'a' if t[idx] == 'b' else 'b'
        
        return {
            'n': self.n,
            's': ''.join(s),
            't': ''.join(t)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        t = question_case['t']
        prompt = f"""You are Monocarp trying to make two strings s and t equal. Both strings have a length of {n} and consist only of lowercase letters 'a' and 'b'. You can perform any number of the following operation: choose an index pos_1 in string s and an index pos_2 in string t, then swap the character at s[pos_1] with the character at t[pos_2]. Your goal is to determine the minimum number of operations required to make the two strings equal, and provide one such optimal sequence of operations. If it is impossible, output -1.

Input:

The first line contains the integer n: {n}.
The second line is string s: {s}.
The third line is string t: {t}.

Output:

If impossible, output -1. Otherwise, output the minimum number of operations k on the first line, followed by k lines each containing two integers pos_1 and pos_2 (1-based indices).

Please format your answer as follows:

[answer]
k
pos_1 pos_2
...
[/answer]

Ensure your answer is enclosed within [answer] and [/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

