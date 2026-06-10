import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from typing import List
from typing import Tuple
from typing import Union




class DcuptrickInstructionGenerator(BaseInstructionGenerator):
    """Dcuptrick Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dcuptrick指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(2, 5))
        self.m = params.get('m', random.randint(1, 3))
        self.valid_probability = params.get('valid_probability', 0.5)
    
    def case_generator(self):
        n = self.n
        m = self.m
        operations = []
        for _ in range(m):
            x = random.randint(1, n)
            y = random.randint(1, n)
            operations.append((x, y))
        
        expected_solution = self.solve(n, m, operations)
        return {
            'n': n,
            'm': m,
            'operations': operations,
            'expected_solution': expected_solution
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        operations = question_case['operations']
        input_example = f"{n} {m}\n" + "\n".join(f"{x} {y}" for x, y in operations)
        problem = (
            "The employees of the F company witnessed a magician's trick with cups and a marble. "
            "Your task is to determine the initial permutation of cups or state it's impossible.\n\n"
            
            "Rules:\n"
            "1. Cups are numbered 1 to n. Each operation moves the cup at position yi to the front.\n"
            "2. Given m operations in order, find the lexicographically smallest initial permutation.\n"
            "3. If impossible, output -1.\n\n"
            
            "Input:\n"
            f"{input_example}\n\n"
            
            "Output:\n"
            "The lexicographically smallest initial permutation or -1.\n\n"
            
            "Format your answer within [answer] and [/answer]. Example: [answer]2 1 3[/answer] or [answer]-1[/answer]."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n: int, m: int, operations: List[Tuple[int, int]]) -> Union[List[int], int]:
        val = [-1] * n
        used = [False] * n
        current = list(range(n))
        valid = True

        for op in operations:
            x, y = op
            x -= 1  # 0-based
            y -= 1

            if y >= len(current):
                valid = False
                break
            opos = current[y]

            if val[opos] != -1:
                if val[opos] != x:
                    valid = False
                    break
            else:
                if used[x]:
                    valid = False
                    break
                val[opos] = x
                used[x] = True

            # Move to front
            current.pop(y)
            current.insert(0, opos)

        if not valid:
            return -1

        j = 0
        for i in range(n):
            if val[i] == -1:
                while j < n and used[j]:
                    j += 1
                if j >= n:
                    return -1
                val[i] = j
                used[j] = True

        solution = [v + 1 for v in val]
        return solution
