import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def preprocess_nxt(s):
    n = len(s)
    nx = [-1] * 26
    nxt = [[-1] * 26 for _ in range(n + 1)]
    for i in range(n, -1, -1):
        if i < n:
            c = ord(s[i]) - ord('a')
            nx[c] = i + 1
        for j in range(26):
            nxt[i][j] = nx[j]
    return nxt

def trans(nxt, k, d):
    return -1 if k == -1 else nxt[k][d]

def better(a, b):
    if a == -1:
        return b
    if b == -1:
        return a
    return min(a, b)

def simulate_operations(s, operations):
    nxt = preprocess_nxt(s)
    dp = [[[-1 for _ in range(251)] for _ in range(251)] for __ in range(251)]
    dp[0][0][0] = 0
    st1, st2, st3 = [], [], []
    c1, c2, c3 = 0, 0, 0
    expected_outputs = []
    for op in operations:
        parts = op.split()
        cmd, id = parts[0], int(parts[1])
        if cmd == '+':
            d = ord(parts[2]) - ord('a')
            if id == 1:
                st1.append(d)
                new_c1 = c1 + 1
                for i in range(c2 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[c1][i][j], d)
                        if i > 0:
                            di = st2[i-1]
                            val = better(val, trans(nxt, dp[new_c1][i-1][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[new_c1][i][j-1], dj))
                        dp[new_c1][i][j] = val
                c1 += 1
            elif id == 2:
                st2.append(d)
                new_c2 = c2 + 1
                for i in range(c1 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[i][c2][j], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][new_c2][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[i][new_c2][j-1], dj))
                        dp[i][new_c2][j] = val
                c2 += 1
            else:
                st3.append(d)
                new_c3 = c3 + 1
                for i in range(c1 + 1):
                    for j in range(c2 + 1):
                        val = trans(nxt, dp[i][j][c3], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][j][new_c3], di))
                        if j > 0:
                            dj = st2[j-1]
                            val = better(val, trans(nxt, dp[i][j-1][new_c3], dj))
                        dp[i][j][new_c3] = val
                c3 += 1
        else:
            if id == 1:
                st1.pop()
                c1 -= 1
            elif id == 2:
                st2.pop()
                c2 -= 1
            else:
                st3.pop()
                c3 -= 1
        current_dp = dp[c1][c2][c3]
        expected_outputs.append('YES' if current_dp != -1 else 'NO')
    return expected_outputs


class DthreereligionsInstructionGenerator(BaseInstructionGenerator):
    """Dthreereligions Bootcamp指令生成器"""
    
    def __init__(self, max_n=100000, max_q=1000, max_op_len=250):
        """
        初始化Dthreereligions指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_op_len: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_op_len = max_op_len
    
    def case_generator(self):
        n = random.randint(5, 10)
        q = random.randint(5, 10)
        s = ''.join(random.choice(ascii_lowercase) for _ in range(n))
        operations = []
        len1, len2, len3 = 0, 0, 0
        for _ in range(q):
            can_remove = []
            for r in [1, 2, 3]:
                if (r == 1 and len1 > 0) or (r == 2 and len2 > 0) or (r == 3 and len3 > 0):
                    can_remove.append(r)
            can_add = []
            for r in [1, 2, 3]:
                if (r == 1 and len1 < self.max_op_len) or (r == 2 and len2 < self.max_op_len) or (r == 3 and len3 < self.max_op_len):
                    can_add.append(r)
            if not can_add and not can_remove:
                break  # Should not happen with small q
            if can_remove and (random.random() < 0.5 or not can_add):
                r = random.choice(can_remove)
                operations.append(f"- {r}")
                if r == 1:
                    len1 -= 1
                elif r == 2:
                    len2 -= 1
                else:
                    len3 -= 1
            else:
                r = random.choice(can_add)
                c = random.choice(ascii_lowercase)
                operations.append(f"+ {r} {c}")
                if r == 1:
                    len1 += 1
                elif r == 2:
                    len2 += 1
                else:
                    len3 += 1
        expected_outputs = simulate_operations(s, operations)
        return {
            's': s,
            'operations': operations,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        operations = question_case['operations']
        q = len(operations)
        n = len(s)
        problem = (
            "During the archaeological research in the Middle East, you found the traces of three ancient religions. "
            "Each's description evolves through a series of operations. The Word of Universe is a string, and after each evolution, "
            "you need to determine if the three descriptions can form disjoint subsequences of this string.\n\n"
            f"The Word of Universe is '{s}' (length {n}). There are {q} evolutions:\n"
        )
        for op in operations:
            problem += f"{op}\n"
        problem += (
            "\nAfter each evolution, output 'YES' if the three descriptions can coexist peacefully as disjoint subsequences, otherwise 'NO'. "
            "Provide your answers in order, each on a new line. Enclose the entire answer within [answer] and [/answer] tags. "
            "For example:\n"
            "[answer]\n"
            "YES\n"
            "NO\n"
            "...\n"
            "[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

