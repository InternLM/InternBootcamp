import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 9


class CquizRewardCalculator(BaseRewardCalculator):
    """Cquiz奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 保持提取逻辑不变
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 保持验证逻辑不变
        return solution == identity['correct_ans']
    
    # 其他额外方法

