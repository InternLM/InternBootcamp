import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class E1convergingarrayeasyversionInstructionGenerator(BaseInstructionGenerator):
    """E1convergingarrayeasyversion Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化E1convergingarrayeasyversion指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 2)
        self.n_max = params.get('n_max', 5)
        self.c_min = params.get('c_min', 0)
        self.c_max = params.get('c_max', 100)
        self.b_min = params.get('b_min', 0)
        self.b_max = params.get('b_max', 100)
        self.x_min = params.get('x_min', -100000)
        self.x_max = params.get('x_max', 100000)
    
    def case_generator(self):
        # 多策略生成有效案例
        generation_strategies = [
            self._generate_simple_case,
            self._generate_zero_c_case,
            self._generate_max_b_case,
            self._generate_negative_x_case
        ]
        
        for strategy in generation_strategies:
            case = strategy()
            if self._validate_case(case):
                return case
        
        return self._default_case()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # ...保持原有prompt结构，优化问题描述...
        problem_desc = f"""
Calculate the number of valid arrays for given parameters. Put the final answer within [answer] tags.

Problem Parameters:
n = {question_case['n']}
c = {' '.join(map(str, question_case['c']))}
b = {' '.join(map(str, question_case['b']))}
x = {question_case['x']}

Constraints:
- Array a must satisfy 0 ≤ a_i ≤ c_i for all i
- The answer should be modulo {MOD}
- Format answer as: [answer]N[/answer] where N is the computed value

Example Valid Response:
[answer]56[/answer]
"""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_simple_case(self):
        n = random.randint(2, 3)
        c = [random.randint(5, 10) for _ in range(n)]
        b = [random.randint(0, 2) for _ in range(n-1)]
        x = random.randint(-10, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_zero_c_case(self):
        n = 3
        c = [0] + [random.randint(0, 5) for _ in range(n-1)]
        b = [random.randint(0, 5) for _ in range(n-1)]
        x = random.randint(-5, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_max_b_case(self):
        n = random.randint(2, 4)
        c = [random.randint(50, 100) for _ in range(n)]
        b = [100] * (n-1)
        x = random.randint(-100, 0)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _generate_negative_x_case(self):
        n = random.randint(2, 3)
        c = [random.randint(10, 100) for _ in range(n)]
        b = [random.randint(0, 10) for _ in range(n-1)]
        x = random.randint(-1000, -100)
        return {'n':n, 'c':c, 'b':b, 'x':x}

    def _validate_case(self, case):
        try:
            result = self._get_r(case['x'], case['n'], case['c'], case['b'])
            return result >= 0
        except:
            return False

    def _default_case(self):
        return {
            'n': 3,
            'c': [2, 3, 4],
            'b': [2, 1],
            'x': -1
        }

    @staticmethod
    def _check_0(x, n, b):
        d = s = 0
        for i in range(n):
            if i > 0:
                d += b[i-1]
                s += d
            if x*(i+1) + s > 0:
                return False
        return True

    @staticmethod
    def _check_1(x, n, c, b):
        sum_s = 0
        d = s = 0
        for i in range(n):
            sum_s += c[i]
            if i > 0:
                d += b[i-1]
                s += d
            if sum_s < x*(i+1) + s:
                return True
        return False

    @classmethod
    def _compute_dp(cls, x, n, c, b):
        maxN = 10210
        dp = [[0]*maxN for _ in range(n+1)]
        dp[0][0] = 1
        d = s = 0

        for i in range(n):
            if i > 0:
                d += b[i-1]
                s += d
            current_v = x*(i+1) + s
            max_c = c[i]

            # 动态规划优化
            for j in range(maxN):
                if dp[i][j] == 0:
                    continue

                min_val = max(current_v, j)
                max_val = min(j + max_c, maxN-1)

                if min_val > max_val:
                    continue

                # 批量更新区间
                dp[i+1][min_val] = (dp[i+1][min_val] + dp[i][j]) % MOD
                if max_val + 1 < maxN:
                    dp[i+1][max_val+1] = (dp[i+1][max_val+1] - dp[i][j]) % MOD

            # 前缀和优化
            prefix = 0
            for j in range(maxN):
                prefix = (prefix + dp[i+1][j]) % MOD
                dp[i+1][j] = prefix

        return sum(dp[n]) % MOD

    @classmethod
    def _get_r(cls, x, n, c, b):
        # 添加输入验证
        if any(ci < 0 for ci in c):
            raise ValueError("Invalid c array")
        if any(bi < 0 for bi in b):
            raise ValueError("Invalid b array")

        if cls._check_0(x, n, b):
            product = 1
            for ci in c:
                product = (product * (ci + 1)) % MOD
            return product
        if cls._check_1(x, n, c, b):
            return 0
        return cls._compute_dp(x, n, c, b)
