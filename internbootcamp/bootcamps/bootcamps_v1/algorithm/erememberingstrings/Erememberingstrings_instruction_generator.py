import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ErememberingstringsInstructionGenerator(BaseInstructionGenerator):
    """Erememberingstrings Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20, min_m=1, max_m=20, cost_min=0, cost_max=10**6):
        """
        初始化Erememberingstrings指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            cost_min: 参数描述
            cost_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m  # 修正拼写错误
        self.cost_min = cost_min
        self.cost_max = cost_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        m = random.randint(self.min_m, self.max_m)
        strings, cost_matrix = self._generate_valid_case(n, m)
        return {
            'n': n,
            'm': m,
            'strings': strings,
            'cost_matrix': cost_matrix
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['m']}"] + question_case['strings']
        cost_lines = [' '.join(map(str, row)) for row in question_case['cost_matrix']]
        input_str = '\n'.join(input_lines + cost_lines)
        problem = (
            "You need to make strings easy to remember by minimal cost.\n"
            f"Input:\n{input_str}\n"
            "Output the minimal cost within [answer]...[/answer]."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_case(self, n, m):
        # 生成目标字符串：每个字符串至少有一个唯一特征位
        target_strings = []
        pos_pool = list(range(m)) * ((n // m) + 1)
        random.shuffle(pos_pool)

        for i in range(n):
            s = ['x'] * m
            unique_pos = pos_pool[i]
            # 确保该位置字符唯一
            used_chars = set()
            for ts in target_strings:
                used_chars.add(ts[unique_pos])
            while True:
                c = random.choice('abcdefghijklmnopqrstuvwxyz')
                if c not in used_chars:
                    s[unique_pos] = c
                    break
            # 其他位置随机生成
            for j in range(m):
                if j != unique_pos:
                    s[j] = random.choice('abcdefghijklmnopqrstuvwxyz')
            target_strings.append(''.join(s))

        # 构造原始字符串（通过修改目标字符串得到）
        original_strings = []
        cost_matrix = []
        for idx, target in enumerate(target_strings):
            original = list(target)
            modify_pos = random.sample(range(m), k=random.randint(0, m//2))
            costs = []
            for j in range(m):
                if j in modify_pos:
                    # 生成修改成本并改变字符
                    original[j] = random.choice('abcdefghijklmnopqrstuvwxyz'.replace(target[j], ''))
                    costs.append(random.randint(1, 1000))
                else:
                    costs.append(0)
            original_strings.append(''.join(original))
            cost_matrix.append(costs)

        return original_strings, cost_matrix

    @staticmethod
    def calculate_min_cost(n, m, strings, cost_matrix):
        INF = float('inf')
        dp = [INF] * (1 << n)
        dp[0] = 0

        for state in range(1 << n):
            if dp[state] == INF:
                continue

            # Find first unset bit
            bit = None
            for i in range(n):
                if not (state & (1 << i)):
                    bit = i
                    break
            if bit is None:
                continue

            # Try all possible positions
            for j in range(m):
                # Option 1: change current string's j-th character
                new_state = state | (1 << bit)
                cost = dp[state] + cost_matrix[bit][j]
                if dp[new_state] > cost:
                    dp[new_state] = cost

                # Option 2: group change
                same_chars = [bit]
                for k in range(n):
                    if k != bit and strings[k][j] == strings[bit][j]:
                        same_chars.append(k)

                sum_cost = sum(cost_matrix[x][j] for x in same_chars)
                max_cost = max(cost_matrix[x][j] for x in same_chars)
                total_cost = sum_cost - max_cost
                new_state_group = state
                for x in same_chars:
                    new_state_group |= (1 << x)

                if dp[new_state_group] > dp[state] + total_cost:
                    dp[new_state_group] = dp[state] + total_cost

        return dp[(1 << n) - 1]
