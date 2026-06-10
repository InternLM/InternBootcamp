import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CstlRewardCalculator(BaseRewardCalculator):
    """Cstl奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output)
        if matches:
            return matches[-1].strip()
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct_answer = identity['correct_answer']
        return solution == correct_answer
    
    # 其他额外方法

