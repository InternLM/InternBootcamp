import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import comb

# === 源文件中的全局变量 ===

MOD = 998244353


class E2chiorianddollpickinghardversionInstructionGenerator(BaseInstructionGenerator):
    """E2chiorianddollpickinghardversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5):
        """
        初始化E2chiorianddollpickinghardversion指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        m = random.choice([0, 3, 4, 5]) if self.max_m >=5 else random.randint(0, self.max_m)
        n = random.randint(1, self.max_n)
        
        if m == 0:
            a_list = [0] * n
        else:
            a_list = [random.randint(0, (1 << m)-1) for _ in range(n)]
            # 确保有解的情况下至少保留一个非零元素
            if all(x == 0 for x in a_list):
                a_list[random.randint(0, n-1)] = random.randint(1, (1 << m)-1)
        
        expected_output = self.solve_case(n, m, a_list)
        return {
            'n': n,
            'm': m,
            'a': a_list,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        a = question_case['a']
        problem = (
            f"## 问题描述\n"
            f"Chiori有{n}个人偶，每个人偶的值为{a}（每个值都小于2^{m}）。\n"
            f"需要计算所有子集的异或和的二进制表示中1的个数恰好为i的方案数（0 ≤ i ≤ {m}），结果模998244353。\n\n"
            f"## 输出格式\n"
            f"输出{m+1}个空格分隔的整数，分别对应i=0到i={m}的结果，放在[answer]标签内。\n"
            f"示例：\n[answer]1 0 2 3 0 0[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def build_linear_basis(a_list, m):
        basis = [0] * m
        for x in a_list:
            if x == 0:
                continue
            for i in reversed(range(m)):  # 固定从高位到低位处理
                if (x >> i) & 1:
                    if basis[i]:
                        x ^= basis[i]
                    else:
                        basis[i] = x
                        # 消去低位
                        for j in reversed(range(i)):
                            if (basis[i] >> j) & 1:
                                basis[i] ^= basis[j]
                        # 消去高位
                        for j in range(i+1, m):
                            if (basis[j] >> i) & 1:
                                basis[j] ^= basis[i]
                        break
        non_zero = [b for b in basis if b != 0]
        return non_zero, basis

    @staticmethod
    def solve_case(n, m, a_list):
        if m == 0:
            return [pow(2, n, MOD)]

        non_zero, basis = E2chiorianddollpickinghardversionbootcamp.build_linear_basis(a_list, m)
        cnt = len(non_zero)
        pow2 = pow(2, n - cnt, MOD)
        result = [0]*(m+1)

        if 2 * cnt <= m:
            f = [0]*(m+1)

            def dfs(val, idx):
                if idx == cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs(val, idx+1)
                dfs(val ^ non_zero[idx], idx+1)

            dfs(0, 0)
            for i in range(m+1):
                result[i] = (f[i] * pow2) % MOD
        else:
            # 修正组合数计算逻辑
            comb_table = [[0]*(m+1) for _ in range(m+1)]
            for i in range(m+1):
                comb_table[i][0] = 1
                for j in range(1, i+1):
                    comb_table[i][j] = (comb_table[i-1][j] + comb_table[i-1][j-1]) % MOD

            # 构建对偶基
            new_b = []
            for i in range(m):
                cur = 1 << i
                for j in range(m):
                    if basis[j] and ((basis[j] >> i) & 1):
                        cur ^= 1 << j
                if cur != 0:
                    new_b.append(cur)

            dual_cnt = len(new_b)
            f = [0]*(m+1)

            def dfs_dual(val, idx):
                if idx == dual_cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs_dual(val, idx+1)
                dfs_dual(val ^ new_b[idx], idx+1)

            dfs_dual(0, 0)

            inv_pow = pow(2, dual_cnt, MOD)
            inv_pow = pow(inv_pow, MOD-2, MOD)
            total_mul = (pow2 * inv_pow) % MOD

            for i in range(m+1):
                res = 0
                for j in range(m+1):
                    if f[j] == 0:
                        continue
                    tmp = 0
                    for k in range(0, min(i, j)+1):
                        c = (comb_table[j][k] * comb_table[m-j][i-k]) % MOD
                        if k % 2 == 0:
                            tmp = (tmp + c) % MOD
                        else:
                            tmp = (tmp - c) % MOD
                    res = (res + f[j] * tmp) % MOD
                result[i] = (res * total_mul) % MOD

        return [x % MOD for x in result]
