import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class EmatchingvsindependentsetRewardCalculator(BaseRewardCalculator):
    """Ematchingvsindependentset奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_block = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_block: return None
        lines = [l.strip() for l in answer_block[-1].strip().split('\n') if l.strip()]
        try:
            return {
                'type': lines[0], 
                'elements': list(map(int, lines[1].split()))
            } if len(lines)>=2 else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or not solution.get('elements'): return False
        
        n = identity['n']
        elements = solution['elements']
        if len(elements) != n: return False
        
        if solution['type'] == 'Matching':
            edges = identity['edges']
            seen = set()
            for idx in elements:
                if not (1 <= idx <= len(edges)): return False
                u, v = edges[idx-1]
                if u in seen or v in seen: return False
                seen.update({u, v})
            return True
        
        elif solution['type'] == 'IndSet':
            vertices = set(elements)
            if len(vertices) != n: return False
            for u, v in identity['edges']:
                if u in vertices and v in vertices: return False
            return True
        
        return False
    
    # 其他额外方法

