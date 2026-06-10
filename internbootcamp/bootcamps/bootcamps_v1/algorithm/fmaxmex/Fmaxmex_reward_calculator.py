import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class FmaxmexRewardCalculator(BaseRewardCalculator):
    """Fmaxmex奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        return list(map(int, re.findall(r'\[answer\](\d+)\[\/answer\]', output)))
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answers']
    
    # 其他额外方法

