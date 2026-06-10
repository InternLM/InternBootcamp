import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DdirtydeedsdonedirtcheapRewardCalculator(BaseRewardCalculator):
    """Ddirtydeedsdonedirtcheap奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            t = int(lines[0])
            indices = list(map(int, lines[1].split()))
            if len(indices) != t or len(set(indices)) != t:
                return None
            return indices
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            pairs = identity['pairs']
            n = identity['n']
            sm_count = 0
            bi_count = 0
            for a, b in pairs:
                if a < b:
                    sm_count += 1
                else:
                    bi_count += 1
            t_max = max(sm_count, bi_count)
            if len(solution) != t_max:
                return False
            
            target_group_is_sm = sm_count > bi_count  # 严格大于才选SM组
            
            for idx in solution:
                if idx < 1 or idx > len(pairs):
                    return False
                a, b = pairs[idx - 1]
                if target_group_is_sm:
                    if a >= b:
                        return False
                else:
                    if a <= b:
                        return False
            
            sequence = []
            for idx in solution:
                sequence.extend(pairs[idx - 1])
            
            return cls.is_valid_sequence(sequence)
        except:
            return False
    
    # 其他额外方法

