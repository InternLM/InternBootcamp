import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CgeorgeandnumberRewardCalculator(BaseRewardCalculator):
    """Cgeorgeandnumber奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个有效答案
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['n']
    
    # 其他额外方法

