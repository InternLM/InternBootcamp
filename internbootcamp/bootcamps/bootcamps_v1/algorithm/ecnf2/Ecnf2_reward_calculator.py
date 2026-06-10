import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import itertools
import re




class Ecnf2RewardCalculator(BaseRewardCalculator):
    """Ecnf2奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = last_match.splitlines()
        if not lines:
            return None
        first_line = lines[0].strip().upper()
        if first_line == "NO":
            return "NO"
        elif first_line == "YES" and len(lines) >= 2:
            assignment = lines[1].strip()
            return ("YES", assignment)
        else:
            parts = last_match.split()
            if len(parts) >= 2 and parts[0].upper() == "YES":
                return ("YES", parts[1])
            elif len(parts) == 1 and parts[0].upper() == "NO":
                return "NO"
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        m = identity['m']
        clauses = identity['clauses']
        if solution is None:
            return False
        if solution == "NO":
            is_sat, _ = cls.solve_cnf_with_brute_force(identity['n'], m, clauses)
            return not is_sat
        elif isinstance(solution, tuple) and len(solution) == 2 and solution[0].upper() == "YES":
            assignment_str = solution[1]
            if len(assignment_str) != m:
                return False
            if any(c not in '01' for c in assignment_str):
                return False
            assignment = {i+1: int(assignment_str[i]) for i in range(m)}
            for clause in clauses:
                satisfied = any(
                    (lit > 0 and assignment[abs(lit)] == 1) or 
                    (lit < 0 and assignment[abs(lit)] == 0) 
                    for lit in clause
                )
                if not satisfied:
                    return False
            return True
        else:
            return False
    
    # 其他额外方法

