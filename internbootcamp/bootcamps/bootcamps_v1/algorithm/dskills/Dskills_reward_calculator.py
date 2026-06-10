import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DskillsRewardCalculator(BaseRewardCalculator):
    """Dskills奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = [line.strip() for line in last_match.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            max_force = int(lines[0])
            final_levels = list(map(int, lines[1].split()))
            return {'max_force': max_force, 'final_levels': final_levels}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'final_levels' not in solution or 'max_force' not in solution:
            return False
        final_levels = solution['final_levels']
        claimed_force = solution['max_force']
        n = identity['n']
        A = identity['A']
        cf = identity['cf']
        cm = identity['cm']
        m = identity['m']
        a_initial = identity['a_initial']
        
        # 验证长度匹配
        if len(final_levels) != n:
            return False
        
        # 验证等级范围
        if any(af < ai or af > A for af, ai in zip(final_levels, a_initial)):
            return False
        
        # 验证总花费
        total_cost = sum(af - ai for af, ai in zip(final_levels, a_initial))
        if total_cost > m:
            return False
        
        # 计算实际战力值
        perfect_count = sum(1 for af in final_levels if af == A)
        min_level = min(final_levels)
        actual_force = perfect_count * cf + min_level * cm
        
        return actual_force == claimed_force
    
    # 其他额外方法

