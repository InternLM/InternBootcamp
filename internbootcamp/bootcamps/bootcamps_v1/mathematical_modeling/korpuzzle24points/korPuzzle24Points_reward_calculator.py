import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class Korpuzzle24pointsRewardCalculator(BaseRewardCalculator):
    """Korpuzzle24points奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 提取并验证数字使用
            input_nums = sorted(identity['numbers'])
            used_nums = sorted(map(int, re.findall(r'\b\d+\b', solution)))
            if input_nums != used_nums:
                return False
            
            # 数学表达式验证
            expr = solution.replace('×', '*').replace('÷', '/').replace(' ', '')
            return abs(eval(expr) - 24) < 1e-6
        except:
            return False
    
    # 其他额外方法

