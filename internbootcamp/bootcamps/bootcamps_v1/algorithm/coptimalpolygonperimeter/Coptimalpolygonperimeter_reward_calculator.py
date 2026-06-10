import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CoptimalpolygonperimeterRewardCalculator(BaseRewardCalculator):
    """Coptimalpolygonperimeter奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        return answer_blocks[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            solution_values = list(map(int, solution.split()))
            return solution_values == identity['expected_output']
        except:
            return False
    
    # 其他额外方法

