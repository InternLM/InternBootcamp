import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DfibonacciishRewardCalculator(BaseRewardCalculator):
    """Dfibonacciish奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """严格正则匹配"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """精确验证逻辑"""
        return solution == identity['expected']
    
    # 其他额外方法

