import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import comb

# === 源文件中的全局变量 ===

MOD = 998244353


class E2chiorianddollpickinghardversionRewardCalculator(BaseRewardCalculator):
    """E2chiorianddollpickinghardversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return list(map(int, last_match.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_output']
        try:
            if len(solution) != len(expected):
                return False
            return all((s % MOD) == (e % MOD) for s, e in zip(solution, expected))
        except:
            return False
    
    # 其他额外方法

