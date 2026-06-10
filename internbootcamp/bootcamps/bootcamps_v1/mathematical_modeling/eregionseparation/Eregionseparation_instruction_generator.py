import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class EregionseparationInstructionGenerator(BaseInstructionGenerator):
    """Eregionseparation Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=6, **params):
        """
        初始化Eregionseparation指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.min_n = min_n  # 最小城市数量
        self.max_n = max_n  # 最大城市数量
    
    def case_generator(self):
        """生成随机有效的谜题实例"""
        n = random.randint(self.min_n, self.max_n)
        a = [1] * n  # 使用全1数组简化计算
        
        # 生成合法树结构
        p = []
        for city in range(2, n+1):
            p.append(random.randint(1, city-1))  # 父节点必须 <= city-1
        
        return {
            'n': n,
            'a': a,
            'p': p,
            'expected_answer': self._compute_answer(n, a, p)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        p = question_case['p']
        return f"""你是秋之王国的规划师，需要制定区域划分方案。王国包含{n}个城市（编号1-{n}），城市由以下道路连接（每条p_i表示i+1号城市与p_i号城市相连）：{p}。
各城市重要值依次为：{a}。

规则要求：
1. 层级划分必须满足每层区域可继续分割（最后层级除外）
2. 同层级所有区域重要值之和必须相等
3. 区域必须保持连通性

请计算符合要求的划分方案总数（模10^9+7），将最终答案放在[answer][/answer]标签内。例如：
[answer] 42 [/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_answer(n, a_list, p_list):
        """动态计算正确答案"""
        if n == 0:
            return 0

        # 初始化数据结构
        a = [0] * (n + 1)
        for i in range(n):
            a[i+1] = a_list[i]

        # 构建父节点数组
        fa = [0] * (n + 1)
        for idx, parent in enumerate(p_list):
            fa[idx+2] = parent  # p_list对应城市2到n的父节点

        # 自底向上计算子树和
        for i in range(n, 1, -1):
            a[fa[i]] += a[i]

        S = a[1]
        if S == 0:
            return 0

        # 处理a数组
        for i in range(1, n+1):
            a[i] = S // math.gcd(S, a[i])

        # 计算频率数组
        freq = [0] * (n + 2)
        for i in range(1, n+1):
            if a[i] <= n:
                freq[a[i]] += 1

        # 因数叠加
        for i in range(n, 0, -1):
            j = 2 * i
            while j <= n:
                freq[j] += freq[i]
                j += i

        # 动态规划求解
        dp = [0] * (n + 2)
        dp[1] = 1
        ans = 0
        for i in range(1, n+1):
            if freq[i] == i:
                ans = (ans + dp[i]) % MOD
                j = 2 * i
                while j <= n:
                    dp[j] = (dp[j] + dp[i]) % MOD
                    j += i

        return ans % MOD
