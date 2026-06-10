import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class DthreereligionsRewardCalculator(BaseRewardCalculator):
    """Dthreereligions奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip().upper() for line in last_answer.split('\n') if line.strip()]
        valid = all(line in {'YES', 'NO'} for line in lines)
        return lines if valid else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_outputs']
        if not solution or len(solution) != len(expected):
            return False
        return all(s.upper() == e.upper() for s, e in zip(solution, expected))
    
    # 其他额外方法

