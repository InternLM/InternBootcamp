import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
import re




class EpartyRewardCalculator(BaseRewardCalculator):
    """Eparty奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        answer = matches[-1].strip().split()
        if len(answer) < 2:
            return None
        
        try:
            steps = int(answer[0])
            sequence = list(map(int, answer[1:1+steps]))
            if len(sequence) != steps:
                return None
            return {'steps': steps, 'sequence': sequence}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            edges = identity['edges']
            min_steps = cls._solve_min_steps(n, edges)
            
            user_steps = solution.get('steps', -1)
            sequence = solution.get('sequence', [])
            
            if user_steps != min_steps or len(sequence) != min_steps:
                return False
            
            # Simulate the process
            edge_set = set(tuple(sorted(e)) for e in edges)
            for a in sequence:
                friends = set()
                for u, v in edge_set:
                    if u == a:
                        friends.add(v)
                    elif v == a:
                        friends.add(u)
                
                new_edges = [(u, v) for u in friends for v in friends if u < v]
                edge_set.update(new_edges)
            
            return len(edge_set) == n * (n-1) // 2
        except:
            return False
    
    # 其他额外方法

