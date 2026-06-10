import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CpermutationrecoveryRewardCalculator(BaseRewardCalculator):
    """Cpermutationrecovery奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        if content == '-1':
            return -1
        try:
            return list(map(int, content.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        next_list = identity['next']
        
        if solution == -1:
            return cls._is_case_invalid(n, next_list)
        
        if len(solution) != n or set(solution) != set(range(1, n+1)):
            return False
            
        computed_next = cls.compute_next(solution)
        for i in range(n):
            expected = next_list[i]
            if expected != -1 and computed_next[i] != expected:
                return False
        return True
    
    # 其他额外方法

