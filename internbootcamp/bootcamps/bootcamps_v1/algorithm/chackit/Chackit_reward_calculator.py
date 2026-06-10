import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def f(s):
    N = 0
    p = 0
    L = len(s)
    for i in range(len(s)):
        k = L - i - 1
        for j in range(int(s[i])):
            term1 = 9 * k * (10 ** k) // 2
            term2 = (p + j) * (10 ** k)
            N += term1 + term2
        p += int(s[i])
    return N

def g(N):
    if N == 0:
        return '0'
    s = ''
    L = 200  # 调整为200位
    for i in range(L):
        d = 0
        for j in range(10):
            test_s = s + str(j) + '0' * (L - i - 1)
            current_f = f(test_s)
            if current_f >= N:
                if j > 0:
                    s += str(j-1)
                else:
                    s += '0'  # 处理j=0的情况
                d = 1
                break
        if not d:
            s += '9'
    s = s.lstrip('0') or '0'
    return s

def find_test_case(a):
    s_list = []
    p_list = []
    i = 1
    while True:
        target = i * a
        m = g(target)
        q = f(m) % a
        for idx in range(len(p_list)):
            if q == p_list[idx] and int(m) > int(s_list[idx]):
                l = int(s_list[idx])
                r = int(m) - 1
                return (l, r)
        s_list.append(m)
        p_list.append(q)
        i += 1


class ChackitRewardCalculator(BaseRewardCalculator):
    """Chackit奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 优先提取answer标签内容
        answer_tag = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if answer_tag:
            pair = answer_tag[-1].strip().split()
            if len(pair) == 2:
                try:
                    return (int(pair[0]), int(pair[1]))
                except:
                    pass
        
        # 兜底提取最后的数字对
        digit_pairs = re.findall(r'\b(\d+)\s+(\d+)\b', output)
        if digit_pairs:
            last_pair = digit_pairs[-1]
            try:
                return (int(last_pair[0]), int(last_pair[1]))
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != 2:
            return False
        l, r = solution
        a = identity['a']
        
        # 基本约束检查
        if not (1 <= l <= r < 10**200):
            return False
        if any(len(str(x)) != len(str(int(x))) for x in (l, r)):  # 检查前导零
            return False

        # 优化计算模值
        def compute_mod(n_str, mod):
            total = 0
            pos = 0
            digit_sum = 0
            for ch in reversed(n_str):
                digit = int(ch)
                cnt = digit
                # 0-9的模式重复次数
                full_cycles = cnt * (cnt-1) // 2
                total += (full_cycles * (10**pos)) % mod
                # 当前位贡献
                total += digit_sum * cnt * (10**pos) % mod
                # 更新digit_sum
                digit_sum += digit
                pos += 1
            return total % mod

        try:
            mod_total = (compute_mod(str(r), a) - compute_mod(str(l-1), a)) % a
            return mod_total == 0
        except:
            return False
    
    # 其他额外方法

