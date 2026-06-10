import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import re
import random
from itertools import combinations




class CcaptainmarmotRewardCalculator(BaseRewardCalculator):
    """Ccaptainmarmot奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_answers = list(map(int, solution.strip().split()))
            if len(user_answers) != identity['n']:
                return False
        except:
            return False
        
        for i, regiment in enumerate(identity['regiments']):
            try:
                # Generate all possible rotation states per mole
                rotation_states = []
                for mole in regiment:
                    x, y, a, b = mole
                    states = []
                    current_x, current_y = x, y
                    states.append((current_x, current_y))
                    for _ in range(3):
                        current_x, current_y = a - (current_y - b), b + (current_x - a)
                        states.append((current_x, current_y))
                    rotation_states.append(states)
                
                # Find minimal rotations
                min_rotations = None
                for r0 in range(4):
                    for r1 in range(4):
                        for r2 in range(4):
                            for r3 in range(4):
                                points = [
                                    rotation_states[0][r0],
                                    rotation_states[1][r1],
                                    rotation_states[2][r2],
                                    rotation_states[3][r3]
                                ]
                                if cls._is_valid_square(points):
                                    total = r0 + r1 + r2 + r3
                                    if (min_rotations is None) or (total < min_rotations):
                                        min_rotations = total
                
                correct = min_rotations if min_rotations is not None else -1
                if user_answers[i] != correct:
                    return False
            except:
                return False
        
        return True
    
    # 其他额外方法

