import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CreplacementRewardCalculator(BaseRewardCalculator):
    """Creplacement奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        try:
            return list(map(int, last_answer.split()))
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        return solution == case['expected_output']
    
    # 其他额外方法

