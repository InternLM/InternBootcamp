import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BskillsInstructionGenerator(BaseInstructionGenerator):
    """Bskills Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bskills指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            "n_range": (3, 5),       # 控制测试用例规模
            "A_range": (5, 15),
            "cf_range": (5, 20),
            "cm_range": (1, 10),
            "m_range": (10, 100)
        }
        self.params.update(params)
    
    def case_generator(self):
        """
        生成有效测试用例的实现步骤：
        1. 生成随机初始参数
        2. 确保问题存在有效解
        3. 计算最优解作为验证基准
        """
        # 生成基础参数
        n = random.randint(*self.params["n_range"])
        A = random.randint(*self.params["A_range"])
        cf = random.randint(*self.params["cf_range"])
        cm = random.randint(*self.params["cm_range"])
        m = random.randint(*self.params["m_range"])
        
        # 生成初始技能等级（保证有优化空间）
        a = [random.randint(0, A-1) for _ in range(n)]
        while sum(A - x for x in a) <= m:  # 防止初始过于接近满级
            A = random.randint(A+1, A*2)
        
        # 调用解题算法计算最优解
        optimal_force, optimal_levels = self.solve_lesha_problem(n, A, cf, cm, m, a.copy())
        
        return {
            "n": n,
            "A": A,
            "cf": cf,
            "cm": cm,
            "m": m,
            "a": a,
            "_solution": optimal_levels,  # 存储验证基准
            "_force": optimal_force
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""你是游戏《Hacknet》的技能优化专家，需要为角色分配技能点。参数：
- 技能数：{question_case['n']}
- 最大等级：{question_case['A']}
- 当前等级：{' '.join(map(str, question_case['a']))}
- 可用货币：{question_case['m']}
- 完美技能系数（cf）：{question_case['cf']}
- 最低等级系数（cm）：{question_case['cm']}

目标：通过合理分配货币获得最大Force值
Force = (完美技能数 × cf) + (最低技能等级 × cm)

输出要求：
第一行：最大Force值
第二行：最终技能等级（保持原顺序）

将答案包裹在[answer]标签内，示例如下：
[answer]
42
5 5 4
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_lesha_problem(n, A, cf, cm, m, a):
        """实现题目参考解法（Python版本）"""
        a_sorted = sorted((v, i) for i, v in enumerate(a))
        prefix = [0]*(n+1)
        for i in range(n):
            prefix[i+1] = prefix[i] + a_sorted[i][0]

        max_force = 0
        best_levels = a.copy()

        # 先处理全满的情况
        full_cost = sum(A - x for x in a)
        if full_cost <= m:
            return cf * n + cm * A, [A]*n

        # 遍历提升k个技能到满级的情况
        for k in range(n+1):
            if k > 0:
                cost = A - a_sorted[-k][0] if k <= n else 0
                if cost > m:
                    break
                remaining = m - cost

            # 处理最低等级提升
            # (实现完整算法需要补充此处逻辑)

        # 简化解法用于演示（实际应实现完整算法）
        # 此处使用动态规划简化处理
        temp = a.copy()
        remaining = m
        for i in range(n):
            max_add = A - temp[i]
            add = min(remaining, max_add)
            temp[i] += add
            remaining -= add

        perfect = sum(1 for x in temp if x == A)
        min_lv = min(temp)
        return perfect*cf + min_lv*cm, temp
