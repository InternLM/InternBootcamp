import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CpartialsumsInstructionGenerator(BaseInstructionGenerator):
    """Cpartialsums Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=2000, k_max=10**9, a_max=10**9):
        """
        初始化Cpartialsums指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            k_max: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.k_max = k_max
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(self.n_min, min(10, self.n_max))  # 测试时限制n范围
        k = random.choices([0, 1, self.k_max], weights=[0.3,0.4,0.3], k=1)[0]
        a = [random.randint(0, self.a_max) for _ in range(n)]
        return {
            'n': n,
            'k': k,
            'input_array': a,
            'expected_output': self._generate_expected_output(n, k, a)
        }
    
    @staticmethod
    def prompt_func(case):
        return (
            f"给定数组a，执行k次特定变换操作后的结果。每次操作分为两步：\n"
            f"1. 生成前缀和数组s（每个元素模{MOD}）\n"
            f"2. 用s替换原数组a\n"
            f"输入：n={case['n']}, k={case['k']}\n初始数组：{' '.join(map(str, case['input_array']))}\n"
            f"请输出最终数组，答案格式：[answer]结果[/answer]（示例：[answer]1 2 3[/answer]）"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_expected_output(n, k, a):
        l = [1]
        res = []
        for i in range(n):
            res.append(sum(l[j] * a[i-j] % MOD for j in range(i+1)) % MOD)
            next_l = l[-1] * (i + k) % MOD
            inv_denominator = pow(i+1, MOD-2, MOD)
            l.append(next_l * inv_denominator % MOD)
        return res
