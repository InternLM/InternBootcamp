import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BinairoRewardCalculator(BaseRewardCalculator):
    """Binairo奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        try:
            solution = []
            for line in matches[-1].strip().split('\n'):
                solution.append([int(c) for c in line.split()])
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['solution']
        return solution == expected
    
    # 其他额外方法

