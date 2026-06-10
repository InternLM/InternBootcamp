import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CmarblesRewardCalculator(BaseRewardCalculator):
    """Cmarbles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if matches:
            return matches[-1].strip()
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        path1 = identity['path1']
        path2 = identity['path2']
        
        c2i = {'N':0, 'S':1, 'W':2, 'E':3}
        a = path1[::-1]
        c = []
        for k in a:
            c.append(str(c2i[k] ^ 1))
        c.append('#')
        for k in path2:
            c.append(str(c2i[k]))
        c_str = ''.join(c)
        
        n_total = len(c_str)
        f = [-1] * n_total
        for i in range(1, n_total):
            k = f[i-1]
            while k >= 0 and c_str[i] != c_str[k+1]:
                k = f[k]
            if c_str[i] == c_str[k+1]:
                f[i] = k + 1
            else:
                f[i] = -1
        
        correct_answer = 'YES' if f[-1] == -1 else 'NO'
        return solution.strip().upper() == correct_answer.upper()
    
    # 其他额外方法

