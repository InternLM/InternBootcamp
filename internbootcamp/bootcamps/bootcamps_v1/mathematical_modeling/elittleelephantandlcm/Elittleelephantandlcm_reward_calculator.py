import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class ElittleelephantandlcmRewardCalculator(BaseRewardCalculator):
    """Elittleelephantandlcm奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 强化答案抽取逻辑
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output)
        if matches:
            try:
                return int(matches[-1]) % MOD
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 严格验证答案的正确性
        return solution == identity['correct_answer']
    
    # 其他额外方法

