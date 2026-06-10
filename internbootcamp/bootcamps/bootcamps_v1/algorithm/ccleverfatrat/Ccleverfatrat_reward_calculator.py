import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from functools import reduce

# === 源文件中的全局变量 ===

max_oats = 10**6 + 1



# === 源文件中的全局函数 ===

def create_goals(ws):
    wrapped_ws = []
    for row in ws:
        new_row = [max_oats] + row + [max_oats]
        wrapped_ws.append(new_row)
    goal_oats = []
    pre_goal_oat = [0, 0]
    for idx in range(len(wrapped_ws)-1, -1, -1):
        goal_oat = []
        for jdx in range(1, len(wrapped_ws[idx])-1):
            current_ws = wrapped_ws[idx][jdx]
            left_parent = pre_goal_oat[jdx-1]
            right_parent = pre_goal_oat[jdx]
            goal_value = max(current_ws, min(left_parent, right_parent))
            goal_oat.append(goal_value)
        goal_oats.append(goal_oat)
        pre_goal_oat = [max_oats] + goal_oat + [max_oats]
    goal_oats.reverse()
    return goal_oats

def possible_oats(oats_list, current_ws):
    new_oats = []
    for idx in range(len(current_ws)):
        current_threshold = current_ws[idx]
        available_mass = sum([m for (m, _) in oats_list[idx]])
        if available_mass >= current_threshold:
            left = oats_list[idx-1] if idx > 0 else None
            right = oats_list[idx] if idx < len(oats_list)-1 else None
            new_mass = available_mass
            if left is not None:
                new_left = left + [(new_mass, (idx-1, idx))]
                new_oats.append(new_left)
            if right is not None:
                new_right = right + [(new_mass, (idx, idx+1))]
                new_oats.append(new_right)
    return new_oats

def is_break_all(goal_layer, oats_list):
    for idx, threshold in enumerate(goal_layer):
        if idx >= len(oats_list):
            continue
        total_mass = sum([m for (m, _) in oats_list[idx]])
        if total_mass >= threshold:
            return True
    return False

def fatrat(state):
    try:
        a, ws = state['a'], state['ws']
        goals = create_goals(ws)
        current_layer = [[(m, (0, i))] for i, m in enumerate(a)]
        
        for level in range(len(ws)):
            current_goal = goals[level]
            if is_break_all(current_goal, current_layer):
                return "Cerealguy"
            if level == len(ws)-1:
                break
            current_layer = possible_oats(current_layer, ws[level])
            if not current_layer:
                break
        
        final_check = any(len(grp) > 0 for grp in current_layer)
        return "Cerealguy" if final_check else "Fat Rat"
    except:
        return "Fat Rat"


class CcleverfatratRewardCalculator(BaseRewardCalculator):
    """Ccleverfatrat奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output, 
            re.DOTALL
        )
        if not matches:
            return None
        answer = matches[-1].strip()
        if answer.upper() == 'FAT RAT':
            return 'Fat Rat'
        elif answer.upper() == 'CEREALGUY':
            return 'Cerealguy'
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            correct = fatrat(identity)
            return solution == correct
        except:
            return False
    
    # 其他额外方法

