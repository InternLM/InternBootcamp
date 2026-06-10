import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CbanhmiRewardCalculator(BaseRewardCalculator):
    """Cbanhmi奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """鲁棒性答案提取"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return [int(m) for m in matches] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """容错验证逻辑"""
        try:
            expected = identity['answers']
            return solution[-len(expected):] == expected
        except:
            return False
    
    # 其他额外方法

