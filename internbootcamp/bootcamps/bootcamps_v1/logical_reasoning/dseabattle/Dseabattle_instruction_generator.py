import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DseabattleInstructionGenerator(BaseInstructionGenerator):
    """Dseabattle Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dseabattle指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 8)
        self.a = params.get('a', 2)
        self.b = params.get('b', 3)
        self.k = params.get('k', 2)
    
    def case_generator(self):
        while True:
            a = random.randint(1, 3)
            b = random.randint(1, 3)
            min_n = a * b
            max_n = min_n + 10
            n = random.randint(min_n, max_n)
            possible_k_max = n - a * b
            if possible_k_max < 0:
                continue
            k = random.randint(0, possible_k_max)
            ships = self.generate_ships(n, a, b)
            if ships is None:
                continue
            occupied = set()
            for s in ships:
                for i in range(b):
                    occupied.add(s + i)
            available = [i for i in range(n) if i not in occupied]
            if len(available) < k:
                continue
            selected_shots = random.sample(available, k)
            s_list = ['0'] * n
            for idx in selected_shots:
                s_list[idx] = '1'
            s = ''.join(s_list)
            if s.count('1') != k:
                continue
            return {
                'n': n,
                'a': a,
                'b': b,
                'k': k,
                's': s
            }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        b = question_case['b']
        k = question_case['k']
        s = question_case['s']
        prompt = f"""You are playing a one-dimensional Sea Battle game on a 1×{n} grid. There are {a} ships placed on the grid, each consisting of {b} consecutive cells. Ships cannot overlap but can be adjacent. Galya has made {k} shots, all of which missed. Your task is to determine the minimal number of cells to shoot such that at least one ship is hit. The grid is represented by a string of '0's and '1's, where '1's indicate previously shot cells (all misses).

Input format:
The first line contains four integers: n, a, b, k.
The second line contains the string of length n.

For this problem, the input is:
{n} {a} {b} {k}
{s}

Output format:
The first line must contain the minimal number of cells to shoot. The second line must list the cell numbers in any order. Each cell must be numbered from 1 to n.

Please provide your answer within [answer] and [/answer] tags. For example:

[answer]
2
4 2
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_ships(n, a, b):
        occupied = set()
        ships = []
        for _ in range(a):
            possible_starts = []
            for s in range(n - b + 1):
                conflict = False
                for i in range(b):
                    if (s + i) in occupied:
                        conflict = True
                        break
                if not conflict:
                    possible_starts.append(s)
            if not possible_starts:
                return None
            s = random.choice(possible_starts)
            ships.append(s)
            for i in range(b):
                occupied.add(s + i)
        return ships
