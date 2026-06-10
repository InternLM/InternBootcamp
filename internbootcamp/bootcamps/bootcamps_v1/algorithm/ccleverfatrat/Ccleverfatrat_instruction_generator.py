import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CcleverfatratInstructionGenerator(BaseInstructionGenerator):
    """Ccleverfatrat Bootcamp指令生成器"""
    
    def __init__(self, max_n=50, min_weight=1, max_weight=10**6):
        """
        初始化Ccleverfatrat指令生成器
        
        Args:
            max_n: 参数描述
            min_weight: 参数描述
            max_weight: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_weight = min_weight
        self.max_weight = max_weight
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        a = [random.randint(self.min_weight, self.max_weight) for _ in range(n)]
        ws = []
        for i in range(n):
            row_length = n - i
            row = [random.randint(self.min_weight, self.max_weight) for _ in range(row_length)]
            ws.append(row)
        return {'n': n, 'a': a, 'ws': ws}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        desc = (
            "The Fat Rat and Cerealguy's Scale Puzzle\n\n"
            "Structure Rules:\n"
            "1. There are n rows of scales forming a pyramid\n"
            "2. Each scale breaks if oat mass ≥ its capacity\n"
            "3. Broken scales distribute oats to lower scales\n"
            "4. Final result shows if any oats reach the bottom\n\n"
            f"Input:\n- Row count: {question_case['n']}\n"
            f"- Top row oats: {' '.join(map(str, question_case['a']))}\n"
            "Scale capacities:\n"
        )
        for i, row in enumerate(question_case['ws'], 1):
            desc += f"Row {i}: {' '.join(map(str, row))}\n"
        desc += (
            "\nOutput format: Put your answer (either 'Fat Rat' or 'Cerealguy') "
            "between [answer] and [/answer] tags."
        )
        return desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

