import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re
import bisect




class ChackerpackyourbagsRewardCalculator(BaseRewardCalculator):
    """Chackerpackyourbags奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        vouchers = [(v['l'], v['r'], v['cost']) for v in identity['vouchers']]
        return solution == cls.optimal_solution(vouchers, identity['x'])
    
    # 其他额外方法

