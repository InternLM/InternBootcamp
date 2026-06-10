import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import Counter




class CphoenixanddistributionRewardCalculator(BaseRewardCalculator):
    """Cphoenixanddistribution奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*([a-z]+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        # 验证字符匹配
        input_chars = Counter(identity['s'])
        output_chars = Counter(solution)
        if input_chars != output_chars:
            return False

        # 验证正确性
        try:
            sorted_s = ''.join(sorted(identity['s']))
            k = identity['k']
            n = identity['n']
            
            if Counter(solution) != Counter(cls.compute_correct_answer(identity['s'], k)):
                return False

            # 验证字典序正确性
            parts = cls.split_into_parts(sorted_s, k)
            expected_max = max(parts)
            return solution == expected_max
        except Exception:
            return False
    
    # 其他额外方法

