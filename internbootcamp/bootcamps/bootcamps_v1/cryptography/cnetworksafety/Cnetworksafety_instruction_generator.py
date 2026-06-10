import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CnetworksafetyInstructionGenerator(BaseInstructionGenerator):
    """Cnetworksafety Bootcamp指令生成器"""
    
    def __init__(self, max_n=6, max_k=3, **params):
        """
        初始化Cnetworksafety指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = params.get('max_n', max_n)
        self.max_k = params.get('max_k', max_k)
        self.max_m_attempts = params.get('max_m_attempts', 10)
    
    def case_generator(self):
        while True:
            n = random.randint(1, self.max_n)
            k = random.randint(0, self.max_k)
            max_key = (1 << k) - 1 if k > 0 else 0
            c = [random.randint(0, max_key) for _ in range(n)]
            
            # Generate candidate edges with distinct keys
            candidate_edges = set()
            for u in range(n):
                for v in range(u + 1, n):
                    if c[u] != c[v]:
                        candidate_edges.add((u + 1, v + 1))  # 1-based index
            
            # Convert to sorted list for sampling
            candidate_edges = sorted(candidate_edges)
            m_max = min(len(candidate_edges), self.max_m_attempts)
            m = random.randint(0, m_max) if candidate_edges else 0
            
            # Handle edge cases for small n
            selected_edges = []
            if candidate_edges and m > 0:
                selected_edges = random.sample(candidate_edges, m)
            
            # Validate constraints
            if m == 0 or len(selected_edges) == m:
                break
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'c': c,
            'edges': selected_edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        edges_str = '\n'.join(f"{u} {v}" for u, v in case['edges'])
        return (
            "Cnetworksafety Network Security Problem\n\n"
            "**Background**:\n"
            "A virus can flip encryption keys using XOR with an unknown number x. "
            "Find the number of safe (infected subset, x) pairs that keep all communication channels secure.\n\n"
            "**Input Format**:\n"
            f"- Line 1: {case['n']} {case['m']} {case['k']}\n"
            f"- Line 2: {' '.join(map(str, case['c']))}\n"
            f"- Next {case['m']} lines (connections):\n{edges_str}\n\n"
            "**Requirements**:\n"
            "Output the answer modulo 1e9+7\n"
            "Put your final answer within [answer]...[/answer] tags."
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

