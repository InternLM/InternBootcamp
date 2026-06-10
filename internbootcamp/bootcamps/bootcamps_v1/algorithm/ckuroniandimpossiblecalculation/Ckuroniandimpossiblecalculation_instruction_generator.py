import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CkuroniandimpossiblecalculationInstructionGenerator(BaseInstructionGenerator):
    """Ckuroniandimpossiblecalculation Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ckuroniandimpossiblecalculation指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 2)
        self.max_n = params.get('max_n', 20)
        self.min_m = params.get('min_m', 1)
        self.max_m = params.get('max_m', 1000)
        self.a_min = params.get('a_min', 0)
        self.a_max = params.get('a_max', 10**9)
        self.n_gt_m_prob = params.get('n_gt_m_prob', 0.5)
    
    def case_generator(self):
        if random.random() < self.n_gt_m_prob:
            # 确保m的取值范围适配当前max_n
            m_upper = min(self.max_m, self.max_n-1)
            if m_upper < self.min_m:
                m = self.max_n  # 当无法满足则转为生成n <= m模式
                n = random.randint(self.min_n, min(self.max_n, m))
            else:
                m = random.randint(self.min_m, m_upper)
                n = random.randint(m+1, self.max_n)
            a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
            return {
                'n': n,
                'm': m,
                'a': a,
                'expected': 0
            }
        else:
            # 生成n <= m的案例
            m = random.randint(self.min_m, self.max_m)
            n = random.randint(self.min_n, min(self.max_n, m))
            mods = defaultdict(int)
            duplicates = False
            a = []
            for _ in range(n):
                val = random.randint(self.a_min, self.a_max)
                mod = val % m
                if mods[mod] >= 1:
                    duplicates = True
                mods[mod] += 1
                a.append(val)
            
            expected = 0 if duplicates else self._safe_compute(n, m, a)
            return {
                'n': n,
                'm': m,
                'a': a,
                'expected': expected
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_case = f"{question_case['n']} {question_case['m']}\n{' '.join(map(str, question_case['a']))}"
        return f"""编程竞赛题目：
计算所有两两绝对差值的乘积模m

输入格式：
第一行：n m（2≤n≤2e5，1≤m≤1000）
第二行：a_1 a_2 ... a_n（0≤a_i≤1e9）

示例说明：
当n>m时结果为0，否则计算各对差值的乘积取模

当前题目：
输入：
{input_case}

请将最终答案用[answer]标签包裹，例如：[answer]0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _safe_compute(self, n, m, a):
        """安全计算模式（限制n不超过100）"""
        if n > 100:
            return 0
        product = 1
        for i in range(n):
            for j in range(i+1, n):
                product = (product * abs(a[i]-a[j])) % m
        return product
