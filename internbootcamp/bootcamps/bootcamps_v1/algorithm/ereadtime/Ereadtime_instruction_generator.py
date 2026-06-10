import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EreadtimeInstructionGenerator(BaseInstructionGenerator):
    """Ereadtime Bootcamp指令生成器"""
    
    def __init__(self, max_heads=5, max_tracks=5, max_value=10**10):
        """
        初始化Ereadtime指令生成器
        
        Args:
            max_heads: 参数描述
            max_tracks: 参数描述
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_heads = max_heads
        self.max_tracks = max_tracks
        self.max_value = max_value
    
    def case_generator(self):
        n = random.randint(1, self.max_heads)
        m = random.randint(1, self.max_tracks)
        
        # Generate heads with logarithmic distribution
        h = sorted(random.sample(range(1, self.max_value+1), n))
        if n > 1:  # Ensure sorted and unique
            h = sorted(list(set(h)))
            while len(h) < n:
                new_val = random.randint(h[-1]+1, self.max_value)
                h.append(new_val)
        
        # Generate targets with three types of coverage
        p_candidates = set()
        # Type 1: Existing head positions
        p_candidates.update(h)
        # Type 2: Boundary cases (min head ± delta, max head ± delta)
        delta = self.max_value // 1000
        p_candidates.add(max(1, h[0] - delta))
        p_candidates.add(h[0] + delta)
        p_candidates.add(max(1, h[-1] - delta))
        p_candidates.add(h[-1] + delta)
        # Type 3: Random distant points
        for _ in range(max(m, 10)):
            p_candidates.add(random.randint(1, self.max_value))
        
        # Build sorted p list
        p_list = sorted(p_candidates)
        p = []
        for num in p_list:
            if not p or num > p[-1]:
                p.append(num)
            if len(p) == m:
                break
        # Fill remaining with distant values
        while len(p) < m:
            p.append(p[-1] + random.randint(1, self.max_value//100))
        
        return {
            'n': n,
            'm': m,
            'h': h[:n],
            'p': sorted(p[:m])
        }
    
    @staticmethod
    def prompt_func(question_case):
        h = question_case['h']
        p = question_case['p']
        return f"""As a hard drive optimization engineer, determine the minimal time (in seconds) needed to read all required tracks.

Heads (sorted): {h}
Required tracks (sorted): {p}

Rules:
1. Each head can move left/right/stay each second
2. Any track visited by any head (including initial positions) is considered read
3. Find the minimal time where ALL required tracks are covered

Answer format: [answer]{{time}}[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

