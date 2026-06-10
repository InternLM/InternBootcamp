import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DzookeeperandtheinfinitezooRewardCalculator(BaseRewardCalculator):
    """Dzookeeperandtheinfinitezoo奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.I)
        return matches[-1].strip().upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution not in {'YES', 'NO'}:
            return False
        return solution == ('YES' if cls.is_reachable(**identity) else 'NO')
    
    # 其他额外方法

