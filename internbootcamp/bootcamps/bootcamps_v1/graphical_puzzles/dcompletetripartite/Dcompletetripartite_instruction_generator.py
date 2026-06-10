import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DcompletetripartiteInstructionGenerator(BaseInstructionGenerator):
    """Dcompletetripartite Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Dcompletetripartite指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
    
    def case_generator(self):
        # 生成符合题目要求的n范围 (3 ≤ n ≤ 1e5)
        n = random.randint(3, 20)  # 示例使用较小范围便于测试，实际可调至1e5
        
        # 确保三个子集都至少有一个顶点
        sizes = [1, 1, 1]
        remaining = n - 3
        for _ in range(remaining):
            sizes[random.randint(0, 2)] += 1
        
        # 随机分配顶点到三个子集
        vertices = list(range(1, n+1))
        random.shuffle(vertices)
        
        v1 = sorted(vertices[:sizes[0]])
        v2 = sorted(vertices[sizes[0]:sizes[0]+sizes[1]])
        v3 = sorted(vertices[sizes[0]+sizes[1]:])
        
        # 计算跨子集边的总数（数学公式直接计算）
        m = sizes[0]*sizes[1] + sizes[1]*sizes[2] + sizes[2]*sizes[0]
        
        # 生成边集合（仅记录跨子集的边）
        edges = []
        # V1-V2边
        for a in v1:
            edges.extend((min(a,b), max(a,b)) for b in v2)
        # V2-V3边
        for b in v2:
            edges.extend((min(b,c), max(b,c)) for c in v3)
        # V3-V1边
        for c in v3:
            edges.extend((min(c,a), max(c,a)) for a in v1)
        
        # 去重并排序
        edges = sorted(list(set(edges)))
        
        return {
            "n": n,
            "m": len(edges),
            "edges": edges,
            "expected_sets": {
                1: v1,
                2: v2,
                3: v3
            }
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [f"{question_case['n']} {question_case['m']}"]
        input_lines.extend(f"{a} {b}" for a, b in question_case['edges'])
        input_block = "\n".join(input_lines)
        
        prompt = f"""Given an undirected graph with {question_case['n']} vertices and {question_case['m']} edges, determine if the vertices can be partitioned into three non-empty subsets meeting these conditions:

1. All vertices are in exactly one subset
2. For each subset pair (V1,V2), (V2,V3), (V3,V1):
   - No internal edges within either subset
   - Complete bipartite connections between subsets

Input:
{input_block}

Output format:
If possible: {question_case['n']} space-separated integers (1/2/3)
If impossible: -1

Place your final answer between [answer] and [/answer]. Example:
[answer]1 2 2 3 3 3[/answer]"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

