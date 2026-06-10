import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CdimaandstaircaseRewardCalculator(BaseRewardCalculator):
    """Cdimaandstaircase奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        numbers = re.findall(r'\b\d+\b', answer_blocks[-1])
        try:
            return [int(num) for num in numbers]
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_outputs']
        return len(solution) == len(expected) and all(a == b for a, b in zip(solution, expected))
    
    # 其他额外方法

