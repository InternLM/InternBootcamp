import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from math import isqrt




class CprefixproductsequenceRewardCalculator(BaseRewardCalculator):
    """Cprefixproductsequence奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        # Robust extraction with negative lookahead
        pattern = r'\[answer\][\s]*((?!\[answer\]).*?)[\s]*\[/answer\]'
        matches = re.findall(pattern, text, re.DOTALL|re.IGNORECASE)
        if not matches:
            return None
        
        content = matches[-1].strip().upper()
        lines = [l.strip() for l in content.split('\n')]
        
        if lines[0].startswith('NO'):
            return {'answer': 'NO'} if len(lines) == 1 else None
        
        if lines[0].startswith('YES') and len(lines) == int(lines[0][3:].strip() or 0)+1:
            try:
                nums = list(map(int, lines[1:]))
                return {'answer': 'YES', 'sequence': nums}
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        # Structural validation
        if not solution or case['exists'] != (solution.get('answer') == 'YES'):
            return False
        
        if solution['answer'] == 'NO':
            return True
        
        # Numerical validation
        n = case['n']
        seq = solution.get('sequence', [])
        if sorted(seq) != list(range(1, n+1)):
            return False
        
        # Prefix product verification
        seen = set()
        product = 1
        for num in seq:
            product = (product * num) % n
            if product in seen:
                return False
            seen.add(product)
        return seen == set(range(n))
    
    # 其他额外方法

