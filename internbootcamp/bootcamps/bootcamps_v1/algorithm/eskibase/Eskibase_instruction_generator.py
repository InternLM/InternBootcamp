import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

mod = 10**9 + 9


class EskibaseInstructionGenerator(BaseInstructionGenerator):
    """Eskibase Bootcamp指令生成器"""
    
    def __init__(self, n=3, m=4):
        """
        初始化Eskibase指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self):
        # 分离边生成与合并操作的随机性
        edge_rng = random.Random()
        edge_seed = random.getrandbits(32)
        edge_rng.seed(edge_seed)
        
        # 生成边列表
        edges = []
        for _ in range(self.m):
            while True:
                ai = edge_rng.randint(1, self.n)
                bi = edge_rng.randint(1, self.n)
                if ai != bi:
                    edges.append((ai, bi))
                    break
        
        # 创建独立的合并随机生成器
        unite_rng = random.Random()
        unite_seed = random.getrandbits(32)
        unite_rng.seed(unite_seed)
        
        # 计算预期输出
        dsu = list(range(self.n + 1))
        res = 1
        expected_outputs = []
        
        for u, v in edges:
            u_root = self.find_set(dsu, u)
            v_root = self.find_set(dsu, v)
            
            if u_root != v_root:
                expected_outputs.append((res - 1) % mod)
                # 使用独立随机源决定合并方向
                if unite_rng.random() > 0.5:
                    dsu[u_root] = v_root
                else:
                    dsu[v_root] = u_root
            else:
                res = (res * 2) % mod
                expected_outputs.append((res - 1) % mod)
        
        return {
            "n": self.n,
            "m": self.m,
            "edges": edges,
            "expected_outputs": expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_desc = f"{question_case['n']} {question_case['m']}\n" + \
                     '\n'.join(f"{u} {v}" for u, v in question_case['edges'])
        
        return f"""Walrusland滑雪基地建设问题

任务背景：
我们正在规划建设一个滑雪基地网络，包含{question_case['n']}个枢纽（编号1-{question_case['n']}），按顺序修建{question_case['m']}条双向雪道。每次完成道路建设后，需要计算当前所有已建道路中可以组成滑雪基地的方案数（模1000000009）。

滑雪基地定义：
1. 由非空道路集合构成
2. 可以划分为若干闭合路线（track），每个track满足：
   - 闭合路径（起点终点相同）
   - 每条道路最多使用一次
   - 可以使用任意多次枢纽
3. 不同道路集合视为不同的基地

输入格式：
{input_desc}

输出要求：
共输出{question_case['m']}行，每行对应修建完第i条道路后的方案数

请将答案按顺序放在[answer]和[/answer]之间，每行一个数值。例如：
[answer]
0
0
1
3
[/answer]

当前问题输入：
{input_desc}

请计算并输出正确结果：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def find_set(dsu, x):
        if dsu[x] != x:
            dsu[x] = Eskibasebootcamp.find_set(dsu, dsu[x])
        return dsu[x]
