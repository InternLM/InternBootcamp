import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpaintthedigitsRewardCalculator(BaseRewardCalculator):
    """Cpaintthedigits奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().replace(' ', '')
        if answer == '-':
            return '-'
        return answer if all(c in '12' for c in answer) and len(answer) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        digits = list(identity['digits'])
        n = len(digits)
        
        if solution == '-':
            return cls.solve(n, list(map(int, digits))) == '-'
        
        if len(solution) != n or not all(c in '12' for c in solution):
            return False
        
        seq1 = []
        seq2 = []
        for d, c in zip(digits, solution):
            digit = int(d)
            if c == '1':
                seq1.append(digit)
            else:
                seq2.append(digit)
        
        merged = seq1 + seq2
        for i in range(len(merged)-1):
            if merged[i] > merged[i+1]:
                return False
        return True
    
    # 其他额外方法

