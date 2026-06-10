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


class CktreeInstructionGenerator(BaseInstructionGenerator):
    """Cktree Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, min_k=1, max_k=100):
        """
        初始化Cktree指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_k = min_k
        self.max_k = max_k
    
    def case_generator(self):
        # 确保生成的k >=1 且 <=100，d在合法范围内
        k = random.randint(max(1, self.min_k), min(100, self.max_k))
        d = random.randint(1, k)
        # 确保n不超过k的理论可能范围
        max_feasible_n = min(self.max_n, k * 10)  # 合理限制最大n
        n = random.randint(max(1, self.min_n), max_feasible_n)
        return {'n': n, 'k': k, 'd': d}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        d = question_case['d']
        prompt = f"""在k-tree中，每个节点有k个子节点，子节点边的权重分别为1到{k}。请计算从根出发总权重为{n}且至少包含一条权重≥{d}的路径数目（模10^9+7）。
        
输入参数：n={n}, k={k}, d={d}
答案格式：[answer]整数[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(n, k, d):
        # 使用动态规划优化空间复杂度
        dp_total = [0] * (n + 1)
        dp_total[0] = 1
        for i in range(n + 1):
            for j in range(1, k + 1):
                if i + j <= n:
                    dp_total[i + j] = (dp_total[i + j] + dp_total[i]) % MOD

        if d == 1:
            return dp_total[n] % MOD

        dp_no = [0] * (n + 1)
        dp_no[0] = 1
        for i in range(n + 1):
            for j in range(1, d):
                if i + j <= n:
                    dp_no[i + j] = (dp_no[i + j] + dp_no[i]) % MOD

        return (dp_total[n] - dp_no[n]) % MOD
