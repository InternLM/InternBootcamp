import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
from collections import defaultdict




class EmikeandfoamInstructionGenerator(BaseInstructionGenerator):
    """Emikeandfoam Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_q=6, max_ai=20):
        """
        初始化Emikeandfoam指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_ai: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_ai = max_ai
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        q = random.randint(1, self.max_q)
        a = [random.randint(1, self.max_ai) for _ in range(n)]
        queries = [random.randint(1, n) for _ in range(q)]
        return {'n': n, 'q': q, 'a': a, 'queries': queries}
    
    @staticmethod
    def prompt_func(case) -> str:
        return f"""Mike需要管理啤酒货架。现有{case['n']}种啤酒（编号1-{case['n']}），泡沫量分别为：{' '.join(map(str, case['a']))}。
处理{case['q']}次查询（数字表示切换对应啤酒的状态），每次查询后计算货架中满足i<j且gcd(a_i,a_j)=1的啤酒对数。

输入格式：
1行：{case['n']} {case['q']}
2行：{' '.join(map(str, case['a']))}
后续{case['q']}行：{' '.join(map(str, case['queries']))}

将每次查询后的结果依次写在[answer]和[/answer]之间，每个结果占一行。示例：
[answer]
0
2
5
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _compute_expected(cls, n, q, a, queries):
        # 预计算每个数的质因数分解
        prime_factors_list = []
        max_ai = max(a) if a else 1
        sieve = cls._build_sieve(max_ai)

        for num in a:
            factors = set()
            temp = num
            while temp > 1:
                p = sieve[temp]
                factors.add(p)
                while temp % p == 0:
                    temp //= p
            prime_factors_list.append(sorted(factors))

        # 初始化状态
        in_self = defaultdict(bool)
        divi_counts = defaultdict(int)
        current_total = 0
        answer = 0
        output = []

        for x in queries:
            idx = x-1  # queries是1-based
            num = a[idx]
            factors = prime_factors_list[idx]

            if in_self[idx]:
                # 移除操作
                sign = -1
                in_self[idx] = False
            else:
                # 添加操作
                sign = +1
                in_self[idx] = True

            # 计算当前贡献
            coprime_count = 0
            k = len(factors)
            for mask in range(1, 1 << k):
                d = 1
                bits = 0
                for i in range(k):
                    if mask & (1 << i):
                        d *= factors[i]
                        bits += 1
                cnt = divi_counts[d]
                coprime_count += cnt if bits % 2 else -cnt

            delta = sign * (current_total - coprime_count)
            answer += delta
            output.append(answer)

            # 更新除数计数
            for mask in cls._generate_divisors(num):
                divi_counts[mask] += sign

            current_total += sign

        return output

    @staticmethod
    def _build_sieve(max_num):
        sieve = list(range(max_num+1))
        for i in range(2, int(math.sqrt(max_num))+1):
            if sieve[i] == i:
                for j in range(i*i, max_num+1, i):
                    if sieve[j] == j:
                        sieve[j] = i
        return sieve

    @staticmethod
    def _generate_divisors(num):
        if num == 1:
            return []
        divisors = set()
        for i in range(2, int(math.isqrt(num)) + 1):
            if num % i == 0:
                divisors.update({i, num//i})
        divisors.add(num)
        return divisors
