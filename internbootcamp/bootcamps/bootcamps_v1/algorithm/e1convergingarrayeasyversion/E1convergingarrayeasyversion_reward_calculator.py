import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class E1convergingarrayeasyversionRewardCalculator(BaseRewardCalculator):
    """E1convergingarrayeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强模式匹配鲁棒性
        matches = re.findall(r'\[answer\s*\][\n\s]*(-?\d+)[\n\s]*\[/answer\s*\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip()) % MOD
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = cls._get_r(
                identity['x'],
                identity['n'],
                identity['c'],
                identity['b']
            ) % MOD
            return solution == expected
        except:
            return False
    
    # 其他额外方法

