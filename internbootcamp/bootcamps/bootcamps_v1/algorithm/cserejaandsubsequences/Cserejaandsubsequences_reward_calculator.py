import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

MAX_BIT = 20  # 使用20位二进制数表示树状数组大小

TREE_SIZE = 1 << MAX_BIT  # 1048576，覆盖题目最大数值1e6


class CserejaandsubsequencesRewardCalculator(BaseRewardCalculator):
    """Cserejaandsubsequences奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) % MOD if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['correct_answer'] % MOD
        return solution == expected if solution is not None else False
    
    # 其他额外方法

