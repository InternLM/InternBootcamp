import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DomnomandnecklaceInstructionGenerator(BaseInstructionGenerator):
    """Domnomandnecklace Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_k=5):
        """
        初始化Domnomandnecklace指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k
    
    def case_generator(self):
        # 确保k不会超过n的合理范围
        n = random.randint(1, self.max_n)
        max_possible_k = min((n + 1) // 2, self.max_k)  # k最大不超过(n+1)/2
        k = random.randint(1, max_possible_k) if max_possible_k >= 1 else 1
        
        # 生成非空字符串时避免全相同字符导致误判
        chars = [chr(ord('a') + random.randint(0, 25)) for _ in range(n)]
        s = ''.join(chars)
        correct_output = self.solve(n, k, s)
        return {
            'n': n,
            'k': k,
            's': s,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        return (
            "Om Nom needs to cut a bead necklace following specific pattern rules.\n"
            f"Given a string of {question_case['n']} beads: {question_case['s']}\n"
            f"and k = {question_case['k']}, determine for each prefix length (1-{question_case['n']}) "
            "if it forms a regular pattern (A+B+A+B+...+A).\n\n"
            "Output should be a string of '0's and '1's where '1' indicates valid at that position.\n"
            "Put your answer between [answer] and [/answer], e.g.:\n"
            "[answer]010111[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_z(s):
        # 保持与C++完全一致的Z算法实现
        n = len(s)
        z = [0] * n
        z[0] = n  # 空字符匹配整个字符串
        l, r = 0, 0
        for i in range(1, n):
            if i > r:
                l = r = i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
            else:
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    l = i
                    while r < n and s[r - l] == s[r]:
                        r += 1
                    z[i] = r - l
                    r -= 1
        return z

    def solve(self, n, k, s):
        # 移除k=0处理分支
        if k == 0:
            return '0' * n
        z = self.compute_z(s)
        ans = [0] * (n + 2)  # 增加缓冲空间

        for lenAB in range(1, n + 1):
            # 检查前k个B是否满足条件
            valid = True
            current_pos = lenAB
            for _ in range(k - 1):
                if current_pos >= n:
                    valid = False
                    break
                required = lenAB
                if current_pos + required > n:
                    if z[current_pos] < n - current_pos:
                        valid = False
                        break
                else:
                    if z[current_pos] < required:
                        valid = False
                        break
                current_pos += lenAB

            if not valid:
                continue

            # 计算可选A的长度范围
            l = lenAB * k - 1
            if l >= n:
                continue

            a_start = lenAB * k
            if a_start >= n:
                max_a = 0
            else:
                max_a = z[a_start]

            possible_a = min(lenAB, max_a)
            r = l + possible_a

            # 修正差分数组标记
            end = min(r, n)
            ans[l] += 1
            if end < n:
                ans[end + 1] -= 1
            else:
                ans[n] -= 1

        # 重建结果数组
        res = []
        current = 0
        for i in range(n):
            current += ans[i]
            res.append('1' if current > 0 else '0')
        return ''.join(res)
