import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class EpermutationrecoveryRewardCalculator(BaseRewardCalculator):
    """Epermutationrecovery奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        patterns = [
            r'\[answer\]\s*(-?\d[\d\s]*?)\s*\[/answer\]',
            r'answer:\s*(-?\d[\d\s]*)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, output, re.DOTALL)
            if matches:
                last = matches[-1].strip()
                try:
                    return -1 if last == '-1' else list(map(int, last.split()))
                except:
                    continue
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证无解情况
        if solution == -1:
            return not cls.check_solvable(identity['n'], identity['next'])
        
        # 验证排列格式
        n = identity['n']
        if len(solution) != n or set(solution) != set(range(1, n+1)):
            return False

        # 验证next匹配
        expected_next = cls.compute_next(solution)
        for given, actual in zip(identity['next'], expected_next):
            if given != -1 and given != actual:
                return False
        return True
    
    # 其他额外方法

