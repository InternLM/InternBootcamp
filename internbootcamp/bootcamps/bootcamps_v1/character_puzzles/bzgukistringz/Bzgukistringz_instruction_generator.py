import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import Counter
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_max_counts(a, b, c):
    a_counts = [0] * 26
    for char in a:
        a_counts[ord(char) - ord('a')] += 1

    b_counts = [0] * 26
    for char in b:
        b_counts[ord(char) - ord('a')] += 1

    c_counts = [0] * 26
    for char in c:
        c_counts[ord(char) - ord('a')] += 1

    best_bs = 0
    best_cs = 0
    max_total = 0

    # 模拟原题代码，枚举bs到a的长度+1
    max_bs = len(a)
    for bs in range(0, max_bs + 1):
        possible = True
        a_clone = a_counts.copy()
        for i in range(26):
            required = bs * b_counts[i]
            if a_clone[i] < required:
                possible = False
                break
            a_clone[i] -= required
        if not possible:
            continue

        # 计算c的最大次数
        cs = float('inf')
        for i in range(26):
            if c_counts[i] == 0:
                continue
            available = a_clone[i]
            if available < c_counts[i]:
                cs = 0
                break
            cs = min(cs, available // c_counts[i])
        if cs == float('inf'):
            cs = 0

        total = bs + cs
        if total > max_total or (total == max_total and cs > best_cs):
            max_total = total
            best_bs = bs
            best_cs = cs

    return best_bs, best_cs

def count_max_substrings(k_str, b, c):
    subs = []
    len_b, len_c = len(b), len(c)
    if len_b > 0:
        subs.append((len_b, b))
    if len_c > 0 and b != c:
        subs.append((len_c, c))

    n = len(k_str)
    dp = [0] * (n + 1)

    for i in range(n):
        dp[i + 1] = max(dp[i + 1], dp[i])
        for length, sub in subs:
            if i + length > n:
                continue
            if k_str[i:i + length] == sub:
                dp[i + length] = max(dp[i + length], dp[i] + 1)
    return dp[n]


class BzgukistringzInstructionGenerator(BaseInstructionGenerator):
    """Bzgukistringz Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bzgukistringz指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.max_b_length = params.get('max_b_length', 5)
        self.max_c_length = params.get('max_c_length', 5)
        self.max_a_length = params.get('max_a_length', 20)
        self.min_length = params.get('min_length', 1)
        self.max_attempts = params.get('max_attempts', 1000)
    
    def case_generator(self):
        for _ in range(self.max_attempts):
            b = ''.join(random.choices(string.ascii_lowercase, k=random.randint(self.min_length, self.max_b_length)))
            c = ''.join(random.choices(string.ascii_lowercase, k=random.randint(self.min_length, self.max_c_length)))

            a_length = random.randint(max(len(b), len(c), self.min_length), self.max_a_length)
            
            # 确保a至少包含足够的字符生成一个b或一个c
            a_chars = []
            if random.choice([True, False]) and len(b) > 0:
                a_chars.extend(list(b))
            elif len(c) > 0:
                a_chars.extend(list(c))
            
            remaining = a_length - len(a_chars)
            if remaining > 0:
                a_chars += random.choices(string.ascii_lowercase, k=remaining)
            a = ''.join(random.sample(a_chars, len(a_chars)))  # 打乱顺序避免简单排列

            best_bs, best_cs = compute_max_counts(a, b, c)
            if best_bs + best_cs > 0:
                k_str = b * best_bs + c * best_cs
                remaining_chars = []
                a_counter = Counter(a)
                for char in k_str:
                    a_counter[char] -= 1
                for char, count in a_counter.items():
                    remaining_chars.extend([char] * count)
                random.shuffle(remaining_chars)
                k_str += ''.join(remaining_chars)
                
                # 验证生成字符串的字符计数
                if Counter(k_str) != Counter(a):
                    continue
                
                return {
                    'a': a,
                    'b': b,
                    'c': c,
                    'best_bs': best_bs,
                    'best_cs': best_cs,
                    'max_total': best_bs + best_cs
                }
        
        raise RuntimeError("Failed to generate valid case after multiple attempts")
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        b = question_case['b']
        c = question_case['c']
        return f'''GukiZ教授有一个字符串重组谜题需要解决。给定三个字符串a、b、c，你需要将a中的字符重新排列，生成新字符串k，使得k中包含尽可能多的非重叠子串b或c。子串不能重叠，且必须完全匹配。

输入：
a = "{a}"
b = "{b}"
c = "{c}"

请输出重组后的字符串k，确保其是a的一个排列，并将最终答案包裹在[answer]和[/answer]标签中。例如：
[answer]
examplekstring
[/answer]''' 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

