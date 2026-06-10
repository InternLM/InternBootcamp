import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CaliceboborangesandapplesRewardCalculator(BaseRewardCalculator):
    """Caliceboborangesandapples奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        impossible_match = re.search(r'\bImpossible\b', output, re.IGNORECASE)
        if impossible_match:
            return 'Impossible'
        candidates = re.findall(r'(?:\d+[AB])+', output)
        if not candidates:
            return None
        last_candidate = candidates[-1]
        if Caliceboborangesandapplesbootcamp.decompress_solution(last_candidate) is None:
            return None
        return last_candidate
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        x_val = identity['x']
        y_val = identity['y']
        if solution == 'Impossible':
            return not cls.check_solution_exists(x_val, y_val)
        
        decompressed = cls.decompress_solution(solution)
        if decompressed is None:
            return False
        
        alice_orange, alice_apple = 1, 0
        bob_orange, bob_apple = 0, 1
        remaining_oranges = x_val - 1
        remaining_apples = y_val - 1
        
        for c in decompressed:
            if c == 'A':
                needed_o = alice_orange
                needed_a = alice_apple
            elif c == 'B':
                needed_o = bob_orange
                needed_a = bob_apple
            else:
                return False
            
            if remaining_oranges < needed_o or remaining_apples < needed_a:
                return False
            
            remaining_oranges -= needed_o
            remaining_apples -= needed_a
            
            if c == 'A':
                bob_orange += alice_orange
                bob_apple += alice_apple
            else:
                alice_orange += bob_orange
                alice_apple += bob_apple
        
        return (alice_orange + bob_orange == x_val and 
                alice_apple + bob_apple == y_val and
                remaining_oranges == 0 and 
                remaining_apples == 0)
    
    # 其他额外方法

