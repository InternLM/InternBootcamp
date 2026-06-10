import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from functools import reduce
from collections import defaultdict




class ByaroslavandtwostringsRewardCalculator(BaseRewardCalculator):
    """Byaroslavandtwostrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) % Byaroslavandtwostringsbootcamp.mod if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 优化大数运算的分步计算
        s, t = identity['s'], identity['t']
        mod = cls.mod
        
        # 计算总可能性
        total = pow(10, s.count('?') + t.count('?'), mod)
        
        # 并行计算三种量
        leq_st = 1
        leq_ts = 1
        eq = 1
        
        pre_cache = defaultdict(lambda: defaultdict(int))
        # 预计算所有字符组合
        for a in '0123456789?':
            for b in '0123456789?':
                leq = 0
                geq = 0
                equal = 0
                for x in (range(10) if a == '?' else [int(a)]):
                    for y in (range(10) if b == '?' else [int(b)]):
                        leq += (x <= y)
                        geq += (x >= y)
                        equal += (x == y)
                pre_cache['leq'][a+b] = leq % mod
                pre_cache['geq'][a+b] = geq % mod
                pre_cache['eq'][a+b] = equal % mod
        
        for c1, c2 in zip(s, t):
            key = c1 + c2
            leq_st = (leq_st * pre_cache['leq'][key]) % mod
            leq_ts = (leq_ts * pre_cache['geq'][key]) % mod
            eq = (eq * pre_cache['eq'][key]) % mod
        
        correct = (total - leq_st - leq_ts + eq) % mod
        return solution == correct
    
    # 其他额外方法

