import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from itertools import combinations




class AsearchingforgraphRewardCalculator(BaseRewardCalculator):
    """Asearchingforgraph奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answers:
            return None
        edges = set()
        for line in answers[-1].strip().split('\n'):
            u, v = map(int, line.strip().split())
            if u != v:
                edges.add((min(u, v), max(u, v)))
        return sorted(edges)
    
    @classmethod
    def _verify_correction(cls, solution, case):
        # Condition 1: Edge count
        if len(solution) != 2*case['n'] + case['p']:
            return False
        
        # Condition 2: Validate edge structure
        all_nodes = set(range(1, case['n']+1))
        for u, v in solution:
            if u not in all_nodes or v not in all_nodes or u == v:
                return False
        if len(set(solution)) != len(solution):
            return False

        # Condition 3: Generate reference edges and check subset
        ref_edges = set(cls.generate_reference_edges(case['n'], case['p']))
        user_edges = set(solution)
        if not user_edges.issubset(ref_edges):
            return False  # Ensure user edges follow reference structure
        
        return True
    
    # 其他额外方法

