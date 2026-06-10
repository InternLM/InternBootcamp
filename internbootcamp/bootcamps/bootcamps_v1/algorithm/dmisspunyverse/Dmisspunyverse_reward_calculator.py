import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from sys import setrecursionlimit




class DmisspunyverseRewardCalculator(BaseRewardCalculator):
    """Dmisspunyverse奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强答案提取，处理多标签情况"""
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """直接验证数值正确性"""
        return solution == identity['correct_answer']
    
    # 其他额外方法

