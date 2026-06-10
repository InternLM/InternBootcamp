import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from functools import lru_cache




class CdoegraphsRewardCalculator(BaseRewardCalculator):
    """Cdoegraphs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # Extract the last answer block and parse all integers
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        answer_block = answer_blocks[-1]
        # Extract all integers in the block
        answers = list(map(int, re.findall(r'\b\d+\b', answer_block)))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != len(identity['queries']):
            return False
        
        n = identity['n']
        queries = identity['queries']
        limited_n = min(n, 90)  # Reference code limits to 90
        fib = cls.compute_doe_fib(limited_n)
        if len(fib) < limited_n + 1:
            return False  # Invalid Fibonacci sequence
        
        # Convert to tuple for memoization hashability
        fib_tuple = tuple(fib)
        
        for i, (a, b) in enumerate(queries):
            try:
                correct = cls.dfs(a, b, limited_n, fib_tuple)
                if solution[i] != correct:
                    return False
            except:
                return False
        return True
    
    # 其他额外方法

