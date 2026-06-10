import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from bisect import bisect_right

# === 源文件中的全局变量 ===

MOD = 998244353

INF = 10**18


class FarraybeautyRewardCalculator(BaseRewardCalculator):
    """Farraybeauty奖励计算器"""
    
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
        try:
            return solution == cls.compute_answer(
                identity['n'],
                identity['k'],
                identity['a']
            )
        except:
            return False
    
    # 其他额外方法

