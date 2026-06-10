import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

factor_cache = FactorCache()



# === 源文件中的全局函数 ===

def compute_answer(n, a):
    """完全重构的动态规划解法"""
    dp = defaultdict(int)
    dp[0] = 1  # 初始状态：空序列
    total = 0
    
    for num in a:
        factors = sorted(factor_cache.get_factors(num), reverse=True)
        for f in factors:
            if f == 0:
                continue
            prev = f - 1
            if prev in dp:
                contribution = dp[prev]
                total = (total + contribution) % MOD
                dp[f] = (dp[f] + contribution) % MOD
                
    return total



# === 源文件中的其他类 ===

class FactorCache:
    """优化后的因数缓存机制"""
    def __init__(self):
        self.cache = defaultdict(set)
    
    def get_factors(self, n):
        if n not in self.cache:
            factors = set()
            if n > 0:
                max_factor = int(math.isqrt(n))
                step = 2 if n % 2 else 1
                for i in range(1, max_factor + 1, step):
                    if n % i == 0:
                        factors.add(i)
                        factors.add(n//i)
            self.cache[n] = factors
        return self.cache[n]


class CmultiplicityInstructionGenerator(BaseInstructionGenerator):
    """Cmultiplicity Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_a=100):
        """
        初始化Cmultiplicity指令生成器
        
        Args:
            max_n: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n    # 限制最大数组长度
        self.max_a = max_a    # 限制元素最大值
    
    def case_generator(self):
        import random
        n = random.randint(1, self.max_n)
        a = [random.randint(1, self.max_a) for _ in range(n)]
        return {
            "n": n,
            "a": a,
            "correct_answer": compute_answer(n, a)
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        return f"""请计算以下数组中满足条件的所有非空子序列数量：

条件：子序列的第i个元素（从1开始计数）必须能被i整除

输入数组：
{question_case['n']}
{a_str}

答案请用[answer]标签包裹，例如：[answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

