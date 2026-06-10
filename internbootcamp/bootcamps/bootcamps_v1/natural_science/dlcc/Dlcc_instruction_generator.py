import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from fractions import Fraction

# === 源文件中的全局变量 ===

MOD = 998244353


class DlccInstructionGenerator(BaseInstructionGenerator):
    """Dlcc Bootcamp指令生成器"""
    
    def __init__(self, max_n=2):
        """
        初始化Dlcc指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 控制生成的管道数，默认为2
    
    def case_generator(self):
        # 生成较小的测试用例以确保计算可行
        n = random.randint(2, self.max_n)
        x = []
        current_x = random.randint(-100, 100)
        x.append(current_x)
        for _ in range(n-1):
            current_x += random.randint(1, 10)
            x.append(current_x)
        v = [random.randint(1, 10) for _ in range(n)]
        p = [random.choice([0, 100]) for _ in range(n)]  # 确保概率为0%或100%
        
        expected = self.compute_expected(x, v, p)
        return {
            'n': n,
            'pipes': list(zip(x, v, p)),
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        pipes_desc = "\n".join(
            f"{x} {v} {p}" for x, v, p in question_case['pipes']
        )
        return f"""You are a physicist analyzing the Line Chillland Collider experiment. There are {question_case['n']} pipes emitting protons with given coordinates, speeds, and movement probabilities. 

Task:
Calculate the expected duration until the first proton collision. If no collision occurs, the duration is 0. Express the answer as P⋅Q⁻¹ modulo 998244353.

Input:
{question_case['n']}
{pipes_desc}

Format your answer as [answer]<result>[/answer], replacing <result> with the computed value. For example, use [answer]42[/answer] if the result is 42.

Provide the numerical answer within the tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def compute_expected(self, x, v, p):
        directions = []
        for pi in p:
            if pi == 0:
                directions.append(0)  # 左
            else:
                directions.append(1)  # 右

        min_time = None
        for i in range(len(x)):
            for j in range(i+1, len(x)):
                xi, xj = x[i], x[j]
                vi, vj = v[i], v[j]
                di, dj = directions[i], directions[j]

                # 计算碰撞时间
                if di == 1 and dj == 0:  # i右，j左
                    dx = xj - xi
                    dv = vi + vj
                    time = Fraction(dx, dv)
                elif di == 1 and dj == 1 and vi > vj:  # 同右i更快
                    dx = xj - xi
                    dv = vi - vj
                    time = Fraction(dx, dv)
                elif di == 0 and dj == 0 and vj > vi:  # 同左j更快
                    dx = xj - xi
                    dv = vj - vi
                    time = Fraction(dx, dv)
                else:
                    continue  # 无碰撞可能

                if min_time is None or time < min_time:
                    min_time = time

        if min_time is None:
            return 0
        else:
            P = min_time.numerator
            Q = min_time.denominator
            Q_inv = pow(Q, MOD-2, MOD)
            return (P * Q_inv) % MOD
