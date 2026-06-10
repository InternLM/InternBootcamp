import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CcircularrmqRewardCalculator(BaseRewardCalculator):
    """Ccircularrmq奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = re.compile(r'\[answer\](.*?)\[\/answer\]', re.DOTALL)
        matches = pattern.findall(output)
        if not matches:
            return None
        content = matches[-1].strip()
        solutions = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                try:
                    solutions.append(int(line))
                except:
                    return None
        return solutions
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_outputs']
    
    # 其他额外方法

