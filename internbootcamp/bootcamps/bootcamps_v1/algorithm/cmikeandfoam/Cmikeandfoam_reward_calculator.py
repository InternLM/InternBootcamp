import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CmikeandfoamRewardCalculator(BaseRewardCalculator):
    """Cmikeandfoam奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强答案提取的鲁棒性"""
        answer_pattern = re.compile(r'\[answer\][\s]*(.*?)[\s]*\[/answer\]', re.DOTALL)
        matches = answer_pattern.findall(output)
        
        if not matches:
            return None
        
        # 取最后一个答案块并解析数字
        last_answer = matches[-1].strip()
        valid_numbers = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line and line.isdigit():
                valid_numbers.append(int(line))
        
        return valid_numbers if valid_numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格验证答案顺序和数值"""
        correct = identity.get('correct_output', [])
        return solution == correct
    
    # 其他额外方法

