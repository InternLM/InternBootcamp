import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BjohnnyandgrandmasterInstructionGenerator(BaseInstructionGenerator):
    """Bjohnnyandgrandmaster Bootcamp指令生成器"""
    
    def __init__(self, case_types='balanced'):
        """
        初始化Bjohnnyandgrandmaster指令生成器
        
        Args:
            case_types: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        :param case_types: 'balanced'（混合） | 'special_p1'（强制p=1） | 'large_k'（大指数）
        """
        self.case_types = case_types
    
    def case_generator(self):
        # 生成三种核心测试场景
        if self.case_types == 'special_p1':
            p = 1
            n = random.randint(1, 10**3)
            k_list = [0]*n  # p=1时k没有意义
        elif self.case_types == 'large_k':
            p = random.choice([2,3,5])
            n = random.randint(100, 1000)
            k_list = [random.randint(10**5, 10**6) for _ in range(n)]
        else:  # 通用情况
            p = random.choices([1, random.randint(2,10**6)], weights=[0.3,0.7])[0]
            n = random.randint(1, 10**4)
            k_list = [random.randint(0, 10**6) for _ in range(n)]
        
        return {
            'n': n,
            'p': p,
            'k_list': k_list,
            'answer': self._compute_answer(n, p, k_list)
        }
    
    @staticmethod
    def prompt_func(case):
        problem_desc = f"""Split {case['n']} numbers (p={case['p']}, exponents=[{', '.join(map(str, case['k_list']))}]) into two subsets. The absolute difference of their sums must be minimized. Output the minimal difference modulo {MOD}."""
        format_instruction = "Put your final answer within [answer]...[/answer], like [answer]0[/answer] for difference 0."
        return f"{problem_desc}\n\n{format_instruction}" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_answer(n, p, k_list):
        if p == 1:
            return n % 2  # 所有元素为1的拆分

        k_list.sort(reverse=True)
        balance = 0
        for k in k_list:
            if balance == 0:
                balance = pow(p, k, MOD)
            else:
                balance = (balance - pow(p, k, MOD)) % MOD
        return balance
