import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CmaximumsplittingRewardCalculator(BaseRewardCalculator):
    """Cmaximumsplitting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配最后一个有效答案
        matches = re.findall(r'\[answer\s*]([-]?\d+)\s*\[/answer\s*]', output, re.IGNORECASE)
        valid_matches = [m for m in matches if m.lstrip('-').isdigit()]
        return int(valid_matches[-1]) if valid_matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 重新实现验证逻辑，不依赖预存答案
        n = identity['n']
        expected = identity['expected']
        
        # 双重验证逻辑
        try:
            calc_ans = cls.calculate_answer(cls, n)
            return solution == calc_ans == expected
        except:
            return solution == expected
    
    # 其他额外方法

