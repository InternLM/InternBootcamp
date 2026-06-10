import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def prime_factors(n):
    """返回唯一质因数列表（已排序）"""
    if n == 1:
        return []
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n = n // 2
    i = 3
    max_i = int(n**0.5) + 1
    while i <= max_i and n > 1:
        while n % i == 0:
            factors.add(i)
            n = n // i
            max_i = int(n**0.5) + 1
        i += 2
    if n > 1:
        factors.add(n)
    return sorted(factors)

def generate_correct_output(n, q, a, queries):
    """生成正确的输出序列"""
    mark = defaultdict(bool)
    freq = defaultdict(int)
    ans = 0
    tot = 0
    output = []
    
    for x in queries:
        val = a[x-1]
        factors = prime_factors(val)
        lim = 1 << len(factors)
        
        # 计算互质的元素数量
        tmp = 0
        for mask in range(1, lim):
            bits = bin(mask).count('1')
            sign = 1 if bits % 2 else -1
            product = 1
            for j in range(len(factors)):
                if mask & (1 << j):
                    product *= factors[j]
            tmp += sign * freq[product]
        
        if not mark[x]:
            # 添加操作
            ans += (tot - tmp)
            tot += 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] += 1
            mark[x] = True
        else:
            # 移除操作
            ans -= (tot - 1 - tmp) if val == 1 else (tot - tmp)
            tot -= 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] -= 1
                if freq[product] == 0:
                    del freq[product]
            mark[x] = False
        
        output.append(ans)
    
    return output


class CmikeandfoamInstructionGenerator(BaseInstructionGenerator):
    """Cmikeandfoam Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cmikeandfoam指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.max_beer = params.get('max_beer', 5)
        self.max_queries = params.get('max_queries', 8)
        self.max_foam = params.get('max_foam', 20)
    
    def case_generator(self):
        """生成有效测试案例（保证至少有一个解）"""
        while True:
            try:
                n = random.randint(2, self.max_beer)
                q = random.randint(3, self.max_queries)
                a = [random.randint(1, self.max_foam) for _ in range(n)]
                queries = [random.randint(1, n) for _ in range(q)]
                output = generate_correct_output(n, q, a, queries)
                return {
                    'n': n,
                    'q': q,
                    'a': a,
                    'queries': queries,
                    'correct_output': output
                }
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case):
        """生成符合要求的题目描述"""
        problem_desc = (
            "Mike is a bartender at Rico's bar. Your task is to track beer glasses "
            "on a shelf and calculate coprime pairs after each query.\n\n"
            f"Parameters:\n"
            f"- {question_case['n']} beer types\n"
            f"- {question_case['q']} queries\n"
            f"- Foam amounts: {', '.join(map(str, question_case['a']))}\n"
            f"- Query sequence: {', '.join(map(str, question_case['queries']))}\n\n"
            "Rules:\n"
            "1. For each query, toggle the presence of the specified beer type\n"
            "2. After each query, count all (i,j) pairs where i<j and gcd(a_i, a_j)=1\n"
            "3. Output the count immediately after each query\n\n"
            "Output Format:\n"
            "Put each query's result on a separate line within [answer] tags.\n"
            "Example:\n"
            "[answer]\n0\n1\n3\n5\n6\n2\n[/answer]\n"
            "Now provide the answer for the given queries:"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

