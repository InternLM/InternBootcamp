import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CnezzarandsymmetricarrayRewardCalculator(BaseRewardCalculator):
    """Cnezzarandsymmetricarray奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        markers = ['[answer]', '[/answer]']
        try:
            start = output.rindex(markers[0]) + len(markers[0])
            end = output.index(markers[1], start)
            answer = output[start:end].strip().upper()
            return answer if answer in ('YES', 'NO') else None
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        expected = cls.check_case(identity['n'], identity['d'])
        return solution.upper() == expected
    
    # 其他额外方法

