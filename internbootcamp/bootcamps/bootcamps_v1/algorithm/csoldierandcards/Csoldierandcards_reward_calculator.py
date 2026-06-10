import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CsoldierandcardsRewardCalculator(BaseRewardCalculator):
    """Csoldierandcards奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_str = matches[-1].strip()
        if answer_str == '-1':
            return -1
        parts = answer_str.split()
        if len(parts) != 2:
            return None
        try:
            fights = int(parts[0])
            winner = int(parts[1])
            if winner in (1, 2) and fights >= 0:
                return (fights, winner)
        except:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['player1'].copy()
        b = identity['player2'].copy()
        k1, k2 = len(a), len(b)
        states = set()
        
        def my_hash(k1_val, k2_val, a_list, b_list):
            h = k1_val * 100 + k2_val
            for c in a_list:
                h = h * 10 + c
            for c in b_list:
                h = h * 10 + c
            return h
        
        current_hash = my_hash(k1, k2, a, b)
        states.add(current_hash)
        win = 0
        turn = 0
        
        while True:
            if k1 == 0:
                win = 2
                break
            if k2 == 0:
                win = 1
                break
            
            card1, card2 = a[0], b[0]
            if card1 > card2:
                a.append(b.pop(0))
                a.append(a.pop(0))
                k1 += 1
                k2 -= 1
            else:
                b.append(a.pop(0))
                b.append(b.pop(0))
                k2 += 1
                k1 -= 1
            
            new_hash = my_hash(k1, k2, a, b)
            if new_hash in states:
                win = 0
                break
            states.add(new_hash)
            turn += 1
            
            if k1 == 0 or k2 == 0:
                win = 1 if k2 == 0 else 2
                break
        
        correct = (turn, win) if win else -1
        return solution == correct
    
    # 其他额外方法

