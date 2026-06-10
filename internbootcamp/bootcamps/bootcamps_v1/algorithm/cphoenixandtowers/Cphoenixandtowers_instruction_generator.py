import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from heapq import heapify
from heapq import heappop
from heapq import heappush
import re




class CphoenixandtowersInstructionGenerator(BaseInstructionGenerator):
    """Cphoenixandtowers Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=5, max_x=10):
        """
        初始化Cphoenixandtowers指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_x: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n      # 最大块数
        self.max_m = max_m      # 最大塔数
        self.max_x = max_x      # 单块最大高度
    
    def case_generator(self):
        """生成保证有解的问题实例"""
        # 先决定测试案例类型
        m = random.randint(1, self.max_m)
        n_options = [
            m,  # 每个塔一个块的简单情形
            random.randint(m+1, self.max_n)  # 常规情形
        ]
        n = random.choice(n_options)
        x = random.randint(1, self.max_x)
        
        # 生成保证有解的块列表
        h = [random.randint(1, x) for _ in range(n)]
        
        # 使用贪心算法生成解（数学保证有效性）
        solution = self._solve_phoenix(n, m, x, h)
        
        return {
            'n': n,
            'm': m,
            'x': x,
            'blocks': h,
            'solution': solution
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        """生成标准问题描述"""
        return (
            "Cphoenixandtowers has {n} blocks with heights {blocks} (each ≤{x}).\n"
            "Build exactly {m} towers where:\n"
            "1. Each tower has ≥1 block\n"
            "2. Max height difference between any two towers ≤{x}\n"
            "Output format:\n"
            "[answer]\n"
            "YES\n"
            "y₁ y₂ ... yₙ (tower indices) OR NO\n"
            "[/answer]"
        ).format(**case) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _solve_phoenix(self, n, m, x, h):
        """贪心算法求解器"""
        if n == m:
            return list(range(1, m+1))

        ans = [0] * n
        heap = [(0, i+1) for i in range(m)]
        heapify(heap)

        for i in range(n):
            s, j = heappop(heap)
            ans[i] = j
            heappush(heap, (s + h[i], j))

        return ans
