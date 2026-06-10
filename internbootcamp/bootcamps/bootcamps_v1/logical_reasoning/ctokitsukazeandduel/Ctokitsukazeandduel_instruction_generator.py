import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def validate_case(n, k, s):
    first = [n] * 2
    last = [-1] * 2
    
    for i in range(n):
        a = int(s[i])
        first[a] = min(first[a], i)
        last[a] = max(last[a], i)
    
    # Check immediate win for 0 or 1
    for a in [0, 1]:
        if first[a] <= last[a] and (last[a] - first[a] + 1) <= k:
            return 'tokitsukaze'
    
    # Check draw conditions
    for a in [0, 1]:
        if first[a] > last[a]:
            continue
        
        left_space = first[a]
        right_space = (n-1) - last[a]
        len_a = last[a] - first[a] + 1
        
        if len_a > (k+1) or left_space >= k or right_space >= k:
            return 'once again'
    
    return 'quailty'


class CtokitsukazeandduelInstructionGenerator(BaseInstructionGenerator):
    """Ctokitsukazeandduel Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20, **kwargs):
        """
        初始化Ctokitsukazeandduel指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(2, min_n)  # Prevent n=1 edge case
        self.max_n = max_n
        self.kwargs = kwargs
    
    def case_generator(self):
        while True:
            n = random.randint(self.min_n, self.max_n)
            k = random.randint(1, n)
            s = ''.join(random.choice('01') for _ in range(n))
            
            # Allow all-0 or all-1 cases
            if validate_case(n, k, s) in ['tokitsukaze', 'quailty', 'once again']:
                return {'n': n, 'k': k, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        prompt = f"""## Ctokitsukazeandduel Game Rules
- {n} cards arranged in a row with states: {s} (1=UP, 0=DOWN)
- Players alternate turns (Tokitsukaze first)
- Each turn: flip exactly {k} consecutive cards to same state
- Immediate win if all cards match after move
- 1,000,000,000+ moves = draw

## Your Task
Analyze the initial configuration and determine the game outcome. Put your final answer (exactly one of these) between [answer] tags:
[answer]tokitsukaze[/answer]  
[answer]quailty[/answer]  
[answer]once again[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

