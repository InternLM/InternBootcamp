import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

MAX_BIT = 20  # 使用20位二进制数表示树状数组大小

TREE_SIZE = 1 << MAX_BIT  # 1048576，覆盖题目最大数值1e6


class CserejaandsubsequencesInstructionGenerator(BaseInstructionGenerator):
    """Cserejaandsubsequences Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, max_value=1000):
        """
        初始化Cserejaandsubsequences指令生成器
        
        Args:
            max_n: 参数描述
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = min(max_n, 10**5)     # 题目约束n≤1e5
        self.max_value = min(max_value, 10**6)  # 题目约束ai≤1e6
    
    def case_generator(self):
        """生成符合题目数值范围的测试用例"""
        n = random.randint(1, self.max_n)
        a = [random.randint(1, self.max_value) for _ in range(n)]
        return {
            'n': n,
            'a': a,
            'correct_answer': self.compute_answer(n, a)
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        return f"""给定一个长度为{question_case['n']}的正整数序列：[{a_str}]
        
请按以下规则计算结果：
1. 找出所有不同的非空非递减子序列y
2. 对每个y，统计满足∀i (x_i ≤ y_i)的非空序列x的数量
3. 将结果求和并对1e9+7取模

答案格式要求：将最终答案用[answer]标签包裹，例如：[answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n, a):
        """优化后的正确答案计算"""
        tree = [0] * (TREE_SIZE + 1)  # 固定大小的树状数组

        def lowbit(x): return x & -x

        def get(x):
            res = 0
            while x > 0:
                res = (res + tree[x]) % MOD
                x -= lowbit(x)
            return res

        def update(x, v):
            while x <= TREE_SIZE:
                tree[x] = (tree[x] + v) % MOD
                x += lowbit(x)

        for num in a:
            prefix_sum = get(num)
            # 计算新增值并更新树状数组
            new_val = (prefix_sum * num + num) % MOD
            current = (get(num) - get(num-1)) % MOD  # 获取当前值
            delta = (new_val - current) % MOD
            update(num, delta)

        return get(TREE_SIZE) % MOD  # 查询最大值范围内的总和
