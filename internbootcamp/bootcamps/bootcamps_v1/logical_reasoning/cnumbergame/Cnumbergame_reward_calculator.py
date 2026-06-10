import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import math
import random




class CnumbergameRewardCalculator(BaseRewardCalculator):
    """Cnumbergame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(.*?)\s*\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        last_answer = matches[-1].strip().capitalize()
        return last_answer if last_answer in ['Ashishgup', 'FastestFinger'] else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('correct_answer')
    
    # 其他额外方法

