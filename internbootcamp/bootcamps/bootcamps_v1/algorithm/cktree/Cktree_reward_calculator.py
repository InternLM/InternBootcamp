import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CktreeRewardCalculator(BaseRewardCalculator):
    """Cktree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强正则匹配鲁棒性
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(matches[-1]) % MOD if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n, k, d = identity['n'], identity['k'], identity['d']
            correct = cls.calculate_answer(n, k, d)
            # 统一取模比较（处理负数和大数情况）
            return int(solution) % MOD == correct
        except:
            return False
    
    # 其他额外方法

