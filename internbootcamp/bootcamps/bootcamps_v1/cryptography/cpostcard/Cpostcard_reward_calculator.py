import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CpostcardRewardCalculator(BaseRewardCalculator):
    """Cpostcard奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        encrypted_str = identity['encrypted_str']
        k = identity['k']
        
        if solution == 'Impossible':
            return not cls._is_case_possible(encrypted_str, k)
        
        return (
            len(solution) == k and 
            cls._is_valid_solution(encrypted_str, solution)
        )
    
    # 其他额外方法

