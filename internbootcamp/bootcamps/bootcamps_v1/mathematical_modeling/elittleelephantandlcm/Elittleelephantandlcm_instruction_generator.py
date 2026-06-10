import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class ElittleelephantandlcmInstructionGenerator(BaseInstructionGenerator):
    """Elittleelephantandlcm Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_a=10):
        """
        初始化Elittleelephantandlcm指令生成器
        
        Args:
            max_n: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 控制生成序列的最大长度
        self.max_a = max_a  # 控制生成元素的最大值
    
    def case_generator(self):
        # 生成有效测试用例并预计算正确答案
        n = random.randint(1, self.max_n)
        a = [random.randint(1, self.max_a) for _ in range(n)]
        
        # 确保至少包含一个1的测试用例
        if random.random() < 0.3:
            a[random.randint(0, n-1)] = 1
            
        correct_answer = self._solve(a)
        return {
            "n": n,
            "a": a,
            "correct_answer": correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        # 构造详细的问题描述
        n = question_case['n']
        a = question_case['a']
        problem_text = f"""你是数学问题解决专家，请解决以下模运算组合计数问题：

给定长度n={n}的整数序列a: {' '.join(map(str, a))}
找出满足以下条件的整数序列b的数量（模1,000,000,007）：
1. 每个b_i满足1 ≤ b_i ≤ a_i
2. b序列的LCM等于其最大值

输入格式：n
           a1 a2 ... an
输出格式：输出一个整数

请将最终答案放在[answer]标签内，例如：[answer]123[/answer]"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _solve(a):
        # 优化后的高效解法实现
        if not a:
            return 0

        # 预处理频率统计
        freq = defaultdict(int)
        max_val = max(a) if a else 0
        for num in a:
            freq[num] += 1

        # 构建dist数组
        dist = {}
        current = 0
        for x in range(max_val, 0, -1):
            current += freq.get(x, 0)
            dist[x] = current

        # 预计算所有数的约数
        divisors = defaultdict(list)
        for d in range(1, max_val + 1):
            for multiple in range(d, max_val + 1, d):
                divisors[multiple].append(d)

        ans = 1  # 初始值对应X=1的情况

        # 主计算逻辑
        for X in range(2, max_val + 1):
            divs = divisors.get(X, [])
            sz = len(divs)
            if sz < 1:
                continue

            # 计算big乘积项
            big = 1
            for j in range(sz - 1):
                d_current = divs[j]
                d_next = divs[j+1]
                cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                big = (big * pow(j+1, cnt, MOD)) % MOD

            # 处理最后一个约数项
            last_d = divs[-1]
            big = (big * pow(sz, dist.get(last_d, 0), MOD)) % MOD

            # 计算small乘积项
            small = 1
            if sz >= 2:
                for j in range(sz - 2):
                    d_current = divs[j]
                    d_next = divs[j+1]
                    cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                    small = (small * pow(j+1, cnt, MOD)) % MOD

                second_last_d = divs[-2]
                small = (small * pow(sz-1, dist.get(second_last_d, 0), MOD)) % MOD
            else:
                small = 0

            # 累加有效贡献
            contribution = (big - small) % MOD
            ans = (ans + contribution) % MOD

        return ans % MOD
