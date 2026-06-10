import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CvasilythebearandsequenceRewardCalculator(BaseRewardCalculator):
    """Cvasilythebearandsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_str = matches[-1].strip()
        lines = [line.strip() for line in answer_str.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            k = int(lines[0])
            numbers = list(map(int, lines[1].split()))
            if len(numbers) != k or len(set(numbers)) != k:
                return None
            return {'k': k, 'numbers': sorted(numbers)}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        
        a = identity['a']
        v_max = identity['v_max']
        base = identity['base']
        s_count = identity['s_count']
        sol_k = solution.get('k')
        sol_numbers = solution.get('numbers', [])
        
        # Check k matches optimal subset size
        if sol_k != s_count:
            return False
        
        # Validate numbers exist in array
        if len(sol_numbers) != sol_k or len(set(sol_numbers)) != sol_k:
            return False
        for num in sol_numbers:
            if num not in a:
                return False
        
        # Calculate AND of solution
        current_and = sol_numbers[0]
        for num in sol_numbers[1:]:
            current_and &= num
        
        # Verify AND equals base and v_max
        if current_and != base:
            return False
        
        calculated_v = 0
        temp = current_and
        while temp % 2 == 0 and temp > 0:
            calculated_v += 1
            temp >>= 1
        
        return calculated_v == v_max
    
    # 其他额外方法

