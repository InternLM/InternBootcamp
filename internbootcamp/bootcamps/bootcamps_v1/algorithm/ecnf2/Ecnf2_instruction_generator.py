import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import itertools
import re




class Ecnf2InstructionGenerator(BaseInstructionGenerator):
    """Ecnf2 Bootcamp指令生成器"""
    
    def __init__(self, max_variables=10, max_clauses=20):
        """
        初始化Ecnf2指令生成器
        
        Args:
            max_variables: 参数描述
            max_clauses: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_variables = max_variables
        self.max_clauses = max_clauses
    
    def case_generator(self):
        while True:
            m = random.randint(1, self.max_variables)
            n = random.randint(1, self.max_clauses)
            clauses = []
            var_count = defaultdict(int)
            valid = False
            for _ in range(n):
                clause = []
                current_vars = set()
                k = random.randint(1, 3)
                for _ in range(k):
                    available_vars = [var for var in range(1, m+1) if var_count[var] < 2 and var not in current_vars]
                    if not available_vars:
                        break
                    var = random.choice(available_vars)
                    sign = random.choice([1, -1])
                    lit = var * sign
                    clause.append(lit)
                    current_vars.add(var)
                    var_count[var] += 1
                if clause:
                    clauses.append(clause)
                else:
                    continue
            valid = True
            for var in range(1, m+1):
                if var_count[var] > 2:
                    valid = False
                    break
            if not valid:
                continue
            case = {
                "n": len(clauses),
                "m": m,
                "clauses": clauses
            }
            return case
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        n = question_case['n']
        clauses = question_case['clauses']
        input_lines = [f"{n} {m}"]
        for clause in clauses:
            input_lines.append(f"{len(clause)} " + " ".join(map(str, clause)))
        input_example = '\n'.join(input_lines)
        prompt = f"""In Boolean logic, a formula is in conjunctive normal form (Ecnf2) if it is a conjunction of clauses, where each clause is a disjunction of literals. You are given a Ecnf2 formula where each variable appears in at most two clauses (including its negation).

Your task is to determine if the Ecnf2 is satisfiable. If it is, provide a satisfying assignment for the variables.

Input:
{input_example}

Output:
- If not satisfiable, output "NO".
- If satisfiable, output "YES" followed by a string of {m} digits (0 or 1) representing the values of x1 to xm.

Please place your answer within [answer] and [/answer] tags. For example:
[answer]YES
1101[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_cnf_with_brute_force(n, m, clauses):
        for bits in itertools.product([0, 1], repeat=m):
            assignment = {i+1: bits[i] for i in range(m)}
            all_satisfied = True
            for clause in clauses:
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment[var]
                    if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                        satisfied = True
                        break
                if not satisfied:
                    all_satisfied = False
                    break
            if all_satisfied:
                return (True, bits)
        return (False, None)
