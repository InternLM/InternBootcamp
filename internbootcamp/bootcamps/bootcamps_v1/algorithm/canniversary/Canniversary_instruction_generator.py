import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CanniversaryInstructionGenerator(BaseInstructionGenerator):
    """Canniversary Bootcamp指令生成器"""
    
    def __init__(self, max_k=1000, **params):
        """
        初始化Canniversary指令生成器
        
        Args:
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_k = max_k  # 控制k的生成范围
    
    def case_generator(self):
        for _ in range(100):
            try:
                # 改进的参数生成逻辑
                base = 10**random.randint(0, 12)
                l = random.randint(1, base * 100)
                r = l + random.randint(2, 1000)
                
                # 确保满足题目约束条件
                r = min(r, 10**12)
                if r <= l:
                    continue
                
                max_possible_k = r - l + 1
                if max_possible_k < 2:
                    continue
                
                # 生成k的分布：50%小值，20%极值，30%随机值
                if random.random() < 0.5:
                    k = random.randint(2, min(10, max_possible_k))
                else:
                    k_options = [
                        2, 
                        max_possible_k,
                        random.randint(3, min(max_possible_k, self.max_k))
                    ]
                    k = random.choice(k_options)

                m = random.randint(1, 10**9)
                
                # 计算正确答案
                d = self.calculate_d(r, l, k)
                fib_result = self.fibn(d, m)
                
                return {
                    'm': m,
                    'l': l,
                    'r': r,
                    'k': k,
                    'correct_answer': fib_result % m
                }
            except Exception as e:
                continue
        raise RuntimeError("无法生成有效测试用例")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        params = question_case
        return f"""根据以下参数计算斐波那契最大公约数问题：
- 模数 m = {params['m']}
- 区间 l = {params['l']} 到 r = {params['r']}
- 子集大小 k = {params['k']}

输出最终答案到[answer]标签内""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def calculate_d(cls, r, l, k):
        """改进的二分查找算法"""
        def count(d_val):
            return (r // d_val) - ((l - 1) // d_val)

        left, right = 1, r
        best = 1
        while left <= right:
            mid = (left + right) // 2
            if count(mid) >= k:
                best = mid
                left = mid + 1
            else:
                right = mid - 1
        return best

    @staticmethod
    def fibn(n, m):
        """优化的斐波那契计算（修正索引偏移）"""
        if n == 0: return 0
        a, b = 0, 1
        for _ in range(n-1):
            a, b = b, (a + b) % m
        return b % m
