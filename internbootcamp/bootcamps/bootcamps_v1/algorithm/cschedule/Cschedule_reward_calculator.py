import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CscheduleRewardCalculator(BaseRewardCalculator):
    """Cschedule奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.search(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match: return None
        
        lines = [l.strip() for l in match.group(1).strip().split('\n') if l.strip()]
        if not lines: return None
        
        try:
            k = int(lines[0])
            if k == 0 and len(lines) == 1:
                return "0\n"
            if len(lines) < 2: return None
            indices = list(map(int, lines[1].split()))
            if len(indices) != k: return None
            return f"{k}\n{' '.join(map(str, sorted(indices)))}"
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            k = int(solution.split('\n')[0])
            if k == 0: 
                return len(identity['intervals']) == 0 or all(
                    any(a['r'] > b['l'] for a, b in zip(identity['intervals'], identity['intervals'][1:]))
                )
            
            indices = list(map(int, solution.split('\n')[1].split()))
            sorted_intervals = sorted(
                (x for i, x in enumerate(identity['intervals']) if (i+1) not in indices),
                key=lambda x: x['l']
            )
            return all(x['r'] <= y['l'] for x, y in zip(sorted_intervals, sorted_intervals[1:]))
        except:
            return False
    
    # 其他额外方法

