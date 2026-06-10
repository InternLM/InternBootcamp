import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CkilljoyInstructionGenerator(BaseInstructionGenerator):
    """Ckilljoy Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, a_range=(-4000, 4000), x_range=(-4000, 4000)):
        """
        初始化Ckilljoy指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_range: 参数描述
            x_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_range = a_range
        self.x_range = x_range
    
    def case_generator(self):
        ans_type = random.choices([0, 1, 2], weights=[1, 2, 3])[0]
        if ans_type == 0:
            return self._generate_case_0()
        elif ans_type == 1:
            return random.choice([self._generate_case_1_initial_infect, self._generate_case_1_balance_sum])()
        else:
            return self._generate_case_2()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem = f"""Killjoy的账户（评分固定为{question_case['x']}）已感染COVID-2069病毒。现有{question_case['n']}个其他账户，初始评分为：{question_case['a']}。

感染规则：
1. 初始时只有Killjoy的账户被感染
2. 评分相同的账户会立即相互感染
3. 已感染账户不可恢复

比赛规则：
- 每场比赛中可以选择任意账户参赛
- 参赛账户评分变化总和必须为0
- 评分可变为任意整数

请计算感染所有账户所需的最少比赛次数，并将答案放入[answer]标签内，例如：[answer]1[/answer]。"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_case_0(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        return {'n': n, 'x': x, 'a': [x]*n}

    def _generate_case_1_initial_infect(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        num_infect = random.randint(1, n-1)
        a = [x]*num_infect
        remaining = n - num_infect
        for _ in range(remaining):
            while True:
                ai = random.randint(*self.a_range)
                if ai != x:
                    a.append(ai)
                    break
        random.shuffle(a)
        return {'n': n, 'x': x, 'a': a}

    def _generate_case_1_balance_sum(self):
        for _ in range(100):
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            sum_total = n * x
            a = []
            for _ in range(n-1):
                ai = random.randint(*self.a_range)
                while ai == x:
                    ai = random.randint(*self.a_range)
                a.append(ai)
            last = sum_total - sum(a)
            if last != x and self.a_range[0] <= last <= self.a_range[1]:
                a.append(last)
                return {'n': n, 'x': x, 'a': a}
        return {'n': 2, 'x': 0, 'a': [1, -1]}

    def _generate_case_2(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            a = [random.randint(*self.a_range) for _ in range(n)]
            sum_total = sum(a)
            has_x = x in a
            if not has_x and sum_total != n * x:
                return {'n': n, 'x': x, 'a': a}
