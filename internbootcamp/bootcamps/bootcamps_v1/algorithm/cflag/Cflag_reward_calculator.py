import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from string import ascii_lowercase




class CflagRewardCalculator(BaseRewardCalculator):
    """Cflag奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = list(re.finditer(r'\[answer\](\d+)\[\/answer\]', output))
        if matches:
            return int(matches[-1].group(1))
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct_answer = identity['correct_answer']
        return solution == correct_answer
    
    # 其他额外方法

