import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque




class CicecreamcoloringRewardCalculator(BaseRewardCalculator):
    """Cicecreamcoloring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        
        try:
            c = int(lines[0])
            colors = list(map(int, lines[1].split()))
            return {'c': c, 'colors': colors}
        except (IndexError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'colors' not in solution:
            return False
        colors = solution['colors']
        m = identity['m']
        nodes = identity['nodes']
        
        if len(colors) != m:
            return False
        
        max_si = max(len(node['types']) for node in nodes)
        correct_c = max(max_si, 1)
        if solution.get('c') != correct_c:
            return False
        
        if any(c < 1 or c > correct_c for c in colors):
            return False
        
        edge_set = set()
        for node in nodes:
            types = node['types']
            for i in range(len(types)):
                for j in range(i+1, len(types)):
                    u, v = types[i], types[j]
                    edge_set.add((u-1, v-1))
                    edge_set.add((v-1, u-1))
        
        for u, v in edge_set:
            if colors[u] == colors[v]:
                return False
        return True
    
    # 其他额外方法

