import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re




class CtimofeyandremodulingRewardCalculator(BaseRewardCalculator):
    """Ctimofeyandremoduling奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return -1
        else:
            parts = last_match.split()
            if len(parts) != 2:
                return None
            try:
                x = int(parts[0])
                d = int(parts[1])
                return (x, d)
            except ValueError:
                return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        m = identity['m']
        n = identity['n']
        a = identity['a']
        if solution == -1:
            return False
        else:
            x, d = solution
            if n == 1:
                return x == a[0]
            else:
                correct = [(x + i * d) % m for i in range(n)]
                correct_sorted = sorted(correct)
                a_sorted = sorted(a)
                return correct_sorted == a_sorted
    
    # 其他额外方法

