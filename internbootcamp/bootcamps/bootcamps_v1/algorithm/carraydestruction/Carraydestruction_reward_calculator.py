import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CarraydestructionRewardCalculator(BaseRewardCalculator):
    """Carraydestruction奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return last_match
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        lines = solution.strip().split('\n')
        if not lines:
            return False
        first_line = lines[0].strip().upper()
        n = identity['n']
        a = identity['a']
        if first_line == 'NO':
            return not cls.check_solvable(n, a)
        elif first_line == 'YES':
            if len(lines) < 2:
                return False
            try:
                initial_x = int(lines[1].strip())
            except ValueError:
                return False
            steps = []
            for line in lines[2:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    return False
                try:
                    a1, a2 = map(int, parts)
                except ValueError:
                    return False
                steps.append((a1, a2))
            if len(steps) != n:
                return False
            current_x = initial_x
            remaining = a.copy()
            for step in steps:
                a1, a2 = step
                if a1 + a2 != current_x:
                    return False
                if a1 not in remaining or a2 not in remaining:
                    return False
                try:
                    remaining.remove(a1)
                    remaining.remove(a2)
                except ValueError:
                    return False
                current_x = max(a1, a2)
            return len(remaining) == 0
        else:
            return False
    
    # 其他额外方法

