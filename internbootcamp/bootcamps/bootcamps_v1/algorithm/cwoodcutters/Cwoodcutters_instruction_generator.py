import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from copy import deepcopy




class CwoodcuttersInstructionGenerator(BaseInstructionGenerator):
    """Cwoodcutters Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, max_h=100, max_x_step=100):
        """
        初始化Cwoodcutters指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_h: 参数描述
            max_x_step: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_n < 1:
            raise ValueError("Problem constraint requires n ≥ 1")
        self.min_n = min_n
        self.max_n = max_n
        self.max_h = max_h
        self.max_x_step = max_x_step
    
    def case_generator(self):
        """生成严格递增坐标的树列，确保相邻树间隔≥1"""
        n = random.randint(self.min_n, self.max_n)
        x = []
        current_x = random.randint(1, 10)  # 起始坐标随机
        for _ in range(n):
            x.append(current_x)
            current_x += random.randint(1, self.max_x_step)  # 确保严格递增
        h = [random.randint(1, self.max_h) for _ in range(n)]
        return {'n': n, 'trees': list(map(list, zip(x, h)))}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        trees = question_case['trees']
        input_lines = [f"{x} {h}" for x, h in trees]
        problem_desc = f"""Imagine you are a woodcutter trying to maximize the number of trees cut down under these rules:

1. Each tree can be:
   - Cut to fall left (occupies [{chr(36)}x_i - h_i, {chr(36)}x_i])
   - Cut to fall right (occupies [{chr(36)}x_i, {chr(36)}x_i + h_i])
   - Left standing (occupies point {chr(36)}x_i)
2. Fallen trees' intervals MUST NOT overlap, even at endpoints
3. Trees are given in strictly increasing {chr(36)}x_i order

Input:
{question_case['n']}
{chr(10).join(input_lines)}

What's the maximum number of trees that can be cut? Put ONLY the final number within [answer] tags, like [answer]3[/answer]."""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_optimal(trees):
        """严格实现参考代码的贪心算法逻辑"""
        if len(trees) <= 2:
            return len(trees)

        x = [t[0] for t in trees]
        h = [t[1] for t in trees]
        x_copy = deepcopy(x)  # 防止修改原始数据

        count = 2  # 首尾默认计入
        for i in range(1, len(trees)-1):
            # 优先尝试向左倒
            if x_copy[i] - h[i] > x_copy[i-1]:
                count +=1
            else:
                # 向右倒且不影响下一个
                if x_copy[i] + h[i] < x[i+1]:
                    x_copy[i] += h[i]  # 更新坐标影响后续判断
                    count +=1
        return count
