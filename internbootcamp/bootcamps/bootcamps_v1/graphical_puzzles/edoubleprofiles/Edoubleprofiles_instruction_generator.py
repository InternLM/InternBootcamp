import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class EdoubleprofilesInstructionGenerator(BaseInstructionGenerator):
    """Edoubleprofiles Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20, seed=None):
        """
        初始化Edoubleprofiles指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """增强参数校验逻辑"""
        if min_n < 1:
            raise ValueError("min_n must be ≥ 1")
        super().__init__()  # 显式调用父类初始化
        self.min_n = max(min_n, 1)
        self.max_n = max(max_n, self.min_n)
        self.rng = random.Random(seed)
    
    def case_generator(self):
        """完全重构的用例生成器"""
        n = self.rng.randint(self.min_n, self.max_n)
        
        # 生成所有可能边集
        possible_edges = []
        if n >= 2:
            possible_edges = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1)]
        
        # 安全生成m值
        max_m = len(possible_edges)
        m = self.rng.randint(0, max_m) if max_m > 0 else 0
        
        # 安全采样边集
        edges = []
        if m > 0:
            edges = self.rng.sample(possible_edges, m)
            edges.sort()  # 标准化边存储格式
        
        return {
            'n': n,
            'm': m,
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(case):
        """增强格式稳定性的提示模板"""
        n, m, edges = case['n'], case['m'], case['edges']
        edge_display = '\n'.join(f"{u} {v}" for u, v in edges) if edges else "无"
        
        return f"""## 双子账号检测任务
某社交网络有{n}个注册账号（编号1-{n}），已知{m}对好友关系：\n{edge_display}

**规则**：
1. 两个不同账号i和j互为双子，当且仅当：
   - 对其他所有账号k，要么k同时是i和j的好友，要么k既不是i也不是j的好友
2. 只需统计无序对(i,j)的数量

请计算满足条件的无序对总数，并将最终数值置于[answer]标签内。示例：
正确答案为5时：[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _compute_answer(cls, case):
        """优化哈希算法实现"""
        MOD = 10**18 + 3
        SEED = 29
        n, edges = case['n'], case['edges']

        # 初始化哈希基数
        p = [1] * (n + 2)
        for i in range(1, n+1):
            p[i] = (p[i-1] * SEED) % MOD

        # 构建特征哈希
        h = defaultdict(int)
        for u, v in edges:
            h[u] = (h[u] + p[v]) % MOD
            h[v] = (h[v] + p[u]) % MOD

        # 统计哈希等价类
        counter = defaultdict(int)
        for uid in range(1, n+1):
            counter[h[uid]] += 1

        # 计算等价类贡献
        ans = sum(c * (c-1) // 2 for c in counter.values())

        # 检查直接边贡献
        processed = set()
        for u, v in edges:
            if (u, v) in processed:
                continue
            if (h[u] + p[u]) % MOD == (h[v] + p[v]) % MOD:
                ans += 1
            processed.add((u, v))

        return ans
