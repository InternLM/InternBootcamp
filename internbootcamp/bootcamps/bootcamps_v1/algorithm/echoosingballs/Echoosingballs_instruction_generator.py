import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class EchoosingballsInstructionGenerator(BaseInstructionGenerator):
    """Echoosingballs Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=6, v_min=-5, v_max=5, c_max=3, q_min=1, q_max=3):
        """
        初始化Echoosingballs指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            v_min: 参数描述
            v_max: 参数描述
            c_max: 参数描述
            q_min: 参数描述
            q_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.v_min = v_min
        self.v_max = v_max
        self.c_max = c_max
        self.q_min = q_min
        self.q_max = q_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        v = [random.randint(self.v_min, self.v_max) for _ in range(n)]
        c = [random.randint(1, self.c_max) for _ in range(n)]
        q = random.randint(self.q_min, self.q_max)
        queries = [(random.randint(-5, 5), random.randint(-5, 5)) for _ in range(q)]
        expected_outputs = [self._compute_query(v, c, a, b) for a, b in queries]
        return {
            'n': n,
            'q': q,
            'v': v,
            'c': c,
            'queries': queries,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        q = question_case['q']
        v_str = ' '.join(map(str, question_case['v']))
        c_str = ' '.join(map(str, question_case['c']))
        queries = '\n'.join([f"{a} {b}" for a, b in question_case['queries']])
        return f"""你是一个算法竞赛选手，需要解决以下问题：

给定{n}个球按序排列，每个球有颜色c和值v。现在有{q}个查询，每个查询给出系数a和b。要求对每个查询找出最大子序列值。规则如下：
1. 子序列保持原顺序
2. 第一个球的贡献为v_i × b
3. 后续球如果颜色与前一个相同，贡献为v_i × a，否则为v_i × b

输入数据：
n = {n}, q = {q}
v数组: {v_str}
c数组: {c_str}
查询列表:
{queries}

请计算每个查询的最大价值，并按顺序将结果用换行分隔放在[answer]标签内，例如：
[answer]
结果1
结果2
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_query(v_list, c_list, a, b):
        f = {}
        x = None  # Largest color
        y = None  # Second largest color
        res = 0

        for vi, ci in zip(v_list, c_list):
            other = 0
            if x is not None:
                if ci == x:
                    other = f.get(y, 0) if y is not None else 0
                else:
                    other = f.get(x, 0)

            current = f.get(ci, -float('inf'))
            new_val = other + vi * b
            if current != -float('inf'):
                new_val = max(new_val, current + vi * a)

            f[ci] = max(current, new_val) if current != -float('inf') else new_val
            res = max(res, f[ci])

            # Update color rankings
            colors = sorted(f.items(), key=lambda x: -x[1])
            x = colors[0][0] if colors else None
            y = colors[1][0] if len(colors) > 1 else None

        return max(res, 0)
