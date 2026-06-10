import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class EsubstitutesinnumberRewardCalculator(BaseRewardCalculator):
    """Esubstitutesinnumber奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强模式匹配鲁棒性
        pattern = r'\[answer\][\s\n]*(-?\d+)[\s\n]*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1].strip())
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 添加类型检查
        if not isinstance(solution, int):
            return False
        return solution == cls.compute_answer(identity['s'], identity['queries'])
    
    # 其他额外方法

