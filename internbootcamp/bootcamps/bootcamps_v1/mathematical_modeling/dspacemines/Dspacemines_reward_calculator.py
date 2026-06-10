import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random




class DspaceminesRewardCalculator(BaseRewardCalculator):
    """Dspacemines奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answers = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        return answers[-1].strip() if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        try:
            if solution.strip() == '-1':
                return case['correct_t'] == -1.0
            
            submitted = float(solution)
            correct = case['correct_t']
            if correct == -1.0:
                return False
            return abs(submitted - correct) < 1e-6 or abs(submitted - correct)/correct < 1e-6
        except:
            return False
    
    # 其他额外方法

