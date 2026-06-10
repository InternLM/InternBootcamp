import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EsashaandarrayInstructionGenerator(BaseInstructionGenerator):
    """Esashaandarray Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Esashaandarray指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.m = params.get('m', 5)
        self.max_initial = params.get('max_initial', 5)
        self.max_x = params.get('max_x', 5)
    
    def case_generator(self):
        MOD = 10**9 +7
        
        # Generate initial array
        a_initial = [random.randint(1, self.max_initial) for _ in range(self.n)]
        queries = []
        diff = [0] * (self.n + 2)  # 差分数组(1-based)
        
        # Generate queries ensuring at least one type2
        type2_count = 0
        for _ in range(self.m):
            # Force last query to be type2 if no type2 generated
            if type2_count == 0 and len(queries) == self.m -1:
                t = 2
            else:
                t = random.choice([1,2])
            
            l = random.randint(1, self.n)
            r = random.randint(l, self.n)
            
            if t ==1:
                x = random.randint(1, self.max_x)
                queries.append({'type':1, 'l':l, 'r':r, 'x':x})
                # 关键修复点：移除原条件判断
                diff[l-1] += x
                diff[r] -= x  # 直接修改r位置，无需条件判断
            else:
                queries.append({'type':2, 'l':l, 'r':r})
                type2_count +=1
        
        # 计算delta数组的Prefix Sum
        delta = [0]*self.n
        current_diff =0
        for i in range(self.n):
            current_diff += diff[i]
            delta[i] = current_diff
        
        # 计算expected_outputs
        expected_outputs = []
        for q in queries:
            if q['type'] ==2:
                l, r = q['l'], q['r']
                total =0
                for i in range(l-1, r):
                    a = a_initial[i] + delta[i]
                    total = (total + self.fib_mod(a)) % MOD
                expected_outputs.append(total)
        
        # 确保至少一个type2
        if not expected_outputs:
            l, r = 1, self.n
            total = sum(self.fib_mod(a_initial[i] + delta[i]) for i in range(self.n)) % MOD
            expected_outputs.append(total)
            queries[-1] = {'type':2, 'l':l, 'r':r}
        
        return {
            'n': self.n,
            'm': self.m,
            'initial_array': a_initial,
            'queries': queries,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem_desc = "Sasha has an array of integers and needs to process several queries. Each query is of one of the following types:\n"
        problem_desc += "1. Type 1: Increase all elements from position l to r by x.\n"
        problem_desc += "2. Type 2: Compute the sum of Fibonacci numbers for elements from position l to r, modulo 1e9+7.\n"
        problem_desc += "The Fibonacci numbers are defined as f(1)=1, f(2)=1, f(x)=f(x-1)+f(x-2) for x>2.\n\n"
        problem_desc += f"Initial array: {question_case['initial_array']}\n\n"
        problem_desc += f"Queries (total {len(question_case['queries'])}):\n"
        for idx, q in enumerate(question_case['queries'], 1):
            if q['type'] ==1:
                problem_desc += f"{idx}. Type 1: l={q['l']}, r={q['r']}, x={q['x']}\n"
            else:
                problem_desc += f"{idx}. Type 2: l={q['l']}, r={q['r']}\n"
        problem_desc += "\nFor each Type 2 query, compute the sum of Fibonacci numbers modulo 1e9+7. Provide all answers in the order of the queries, each on a new line enclosed within [answer] and [/answer]. Example:\n[answer]\n5\n7\n9\n[/answer]"
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def fib_mod(x):
        MOD = 10**9 +7
        if x ==0:
            return 0
        if x ==1 or x ==2:
            return 1 % MOD

        def multiply(mat_a, mat_b):
            return [
                [(mat_a[0][0]*mat_b[0][0] + mat_a[0][1]*mat_b[1][0]) % MOD,
                 (mat_a[0][0]*mat_b[0][1] + mat_a[0][1]*mat_b[1][1]) % MOD],
                [(mat_a[1][0]*mat_b[0][0] + mat_a[1][1]*mat_b[1][0]) % MOD,
                 (mat_a[1][0]*mat_b[0][1] + mat_a[1][1]*mat_b[1][1]) % MOD]
            ]

        def matrix_power(mat, power):
            res = [[1,0],[0,1]]
            while power >0:
                if power %2 ==1:
                    res = multiply(res, mat)
                mat = multiply(mat, mat)
                power //=2
            return res

        trans = [[1,1],[1,0]]
        powered = matrix_power(trans, x-2)
        return (powered[0][0] + powered[0][1]) % MOD
