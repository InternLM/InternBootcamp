import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
from collections import defaultdict
from math import gcd




class EcuttingrectangleRewardCalculator(BaseRewardCalculator):
    """Ecuttingrectangle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        rectangles = identity['rectangles']
        if n != len(rectangles):
            return solution == 0  # 异常情况处理
        
        c_list = [r['c'] for r in rectangles]
        total_c = sum(c_list)
        
        cntw = defaultdict(int)
        cnth = defaultdict(int)
        for r in rectangles:
            cntw[r['w']] += r['c']
            cnth[r['h']] += r['c']
        
        valid = all(cntw[r['w']] * cnth[r['h']] == total_c * r['c'] for r in rectangles)
        if not valid:
            return solution == 0
        
        current_gcd = c_list[0]
        for c in c_list[1:]:
            current_gcd = math.gcd(current_gcd, c)
        
        def count_divisors(x):
            if x == 0:
                return 0
            cnt = 0
            sqrt_x = int(math.isqrt(x))
            for i in range(1, sqrt_x + 1):
                if x % i == 0:
                    cnt += 1 if i == x // i else 2
            return cnt
        
        correct = count_divisors(current_gcd)
        return solution == correct
    
    # 其他额外方法

