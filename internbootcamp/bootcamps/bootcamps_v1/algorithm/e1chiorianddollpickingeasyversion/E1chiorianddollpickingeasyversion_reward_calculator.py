import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 998244353


class E1chiorianddollpickingeasyversionRewardCalculator(BaseRewardCalculator):
    """E1chiorianddollpickingeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            extracted = list(map(int, last_match.split()))
            return extracted
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['correct_output']
        return solution == expected
    
    # 其他额外方法

