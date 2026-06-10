import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CwateringflowersRewardCalculator(BaseRewardCalculator):
    """Cwateringflowers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        solution_str = matches[-1].strip()
        try:
            return int(solution_str)
        except ValueError:
            try:
                num = float(solution_str)
                if num.is_integer():
                    return int(num)
            except:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

