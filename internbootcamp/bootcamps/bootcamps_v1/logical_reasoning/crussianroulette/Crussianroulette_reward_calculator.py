import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CrussianrouletteRewardCalculator(BaseRewardCalculator):
    """Crussianroulette奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强模式匹配，允许前后空格
        matches = re.findall(r'\[answer\]\s*([X.]+?)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].upper().replace(' ', '') if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 精确实现参考代码逻辑
        n = identity['n']
        k = identity['k']
        queries = identity['queries']
        
        if k == 0:
            correct = '.' * len(queries)
            return solution == correct
        
        first = n - (2*k -1)
        retr = 0
        if first >= 0:
            if first % 2 == 0:
                retr = 1
                first += 1
            else:
                retr = 0
        else:
            first = 0
        
        res = []
        for q in queries:
            if first > 0:
                if retr and q == n and k > 0:
                    res.append('X')
                elif q <= first:
                    res.append('.')
                else:
                    res.append( 'X' if (q - first) % 2 == 1 else '.' )
            else:
                threshold = 2*(n - k)
                res.append( '.' if q % 2 == 1 and q <= threshold else 'X' )
        
        return solution == ''.join(res)
    
    # 其他额外方法

