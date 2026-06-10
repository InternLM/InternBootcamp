import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import string
import random
import itertools




class BpincodesRewardCalculator(BaseRewardCalculator):
    """Bpincodes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_match = matches[-1].strip()
        parts = [p.strip() for p in last_match.split('\n') if p.strip()]
        
        try:
            k = int(parts[0])
            pins = parts[1:]
            return {'k': k, 'pins': pins}
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'k' not in solution or 'pins' not in solution:
            return False
        
        user_k = solution['k']
        user_pins = solution['pins']
        original = identity['original_pins']
        expected_k = identity['expected_k']
        
        # 基础验证
        if len(user_pins) != len(original):
            return False
        if any(not (len(p) == 4 and p.isdigit()) for p in user_pins):
            return False
        if len(set(user_pins)) != len(user_pins):
            return False
        
        # 计算实际修改次数
        actual_changes = sum(sum(o != u for o, u in zip(orig, user)) 
                           for orig, user in zip(original, user_pins))
        
        # 最终校验需要满足两个条件：
        # 1. 实际修改次数等于用户报告的k
        # 2. 修改次数等于系统计算的最小k 或者 用户k >= 系统k
        return (actual_changes == user_k) and (user_k == expected_k)
    
    # 其他额外方法

