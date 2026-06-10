import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class BplanetlapitulettiRewardCalculator(BaseRewardCalculator):
    """Bplanetlapituletti奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        candidates = re.findall(r'\[answer\](.*?)\[\/answer\]', output, flags=re.I|re.DOTALL)
        for candidate in reversed(candidates):
            candidate = candidate.strip()
            if re.fullmatch(r'\d{2}:\d{2}', candidate):
                return candidate
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 格式严格验证
        if not isinstance(solution, str):
            return False
        if len(solution) != 5 or solution[2] != ':':
            return False
        hh_part, mm_part = solution[:2], solution[3:]
        if not (hh_part.isdigit() and mm_part.isdigit()):
            return False
        
        hh, mm = int(hh_part), int(mm_part)
        if not (0 <= hh < identity['h'] and 0 <= mm < identity['m']):
            return False
        
        # 逻辑一致性验证
        return solution == cls._find_valid_time(identity['h'], identity['m'], identity['s'])
    
    # 其他额外方法

