import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CinterestinggameRewardCalculator(BaseRewardCalculator):
    """Cinterestinggame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_answer = int(solution)
            return user_answer == identity['correct_answer']
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

