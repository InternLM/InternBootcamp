import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import isclose




class DgameRewardCalculator(BaseRewardCalculator):
    """Dgame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output)
        if not matches:
            return None
        solutions = []
        for m in matches:
            m_clean = m.strip()
            # 处理可能的格式问题，例如多余的空格或换行符
            if m_clean == "":
                continue
            try:
                num = float(m_clean)
                solutions.append(num)
            except ValueError:
                pass
        if not solutions:
            return None
        return solutions
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if isinstance(solution, list):
            solutions = solution
        else:
            solutions = [solution]
        n = identity['n']
        size = 2 ** n
        initial_c = identity['initial_c']
        updates = identity['updates']
        r = identity['r']
        correct = []
        current_sum = sum(initial_c)
        correct_value = current_sum / size
        correct.append(correct_value)
        current_c = initial_c.copy()
        for z, g in updates:
            delta = g - current_c[z]
            current_sum += delta
            current_c[z] = g
            correct_value = current_sum / size
            correct.append(correct_value)
        if len(solutions) != len(correct):
            return False
        for s, c in zip(solutions, correct):
            if not isclose(s, c, rel_tol=1e-6, abs_tol=1e-6):
                return False
        return True
    
    # 其他额外方法

