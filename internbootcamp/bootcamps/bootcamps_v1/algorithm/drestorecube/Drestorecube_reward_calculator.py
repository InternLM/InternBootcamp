import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
from itertools import permutations
from itertools import product
from itertools import combinations




class DrestorecubeRewardCalculator(BaseRewardCalculator):
    """Drestorecube奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        # 查找所有匹配的答案块并取最后一个
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answers:
            return None
        answer_block = answers[-1].strip()
        
        lines = [ln.strip() for ln in answer_block.split('\n') if ln.strip()]
        if not lines:
            return None
        
        first_line = lines[0].upper()
        if first_line not in ('YES', 'NO'):
            return None
        
        result = {'result': first_line}
        if first_line == 'YES' and len(lines) != 9:
            return None
        
        if first_line == 'YES':
            points = []
            for ln in lines[1:]:
                parts = ln.split()
                if len(parts) != 3:
                    return None
                try:
                    points.append([int(p) for p in parts])
                except ValueError:
                    return None
            result['points'] = points
        
        return result
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证NO结果
        if solution['result'] == 'NO':
            return not identity.get('solvable', True) and not cls.check_cube_possible(identity['input_points'])
        
        # 验证YES结果
        points = solution.get('points', [])
        if len(points) != 8:
            return False
        
        # 检查排列合法性
        for sol_pt, inp_pt in zip(points, identity['input_points']):
            if sorted(sol_pt) != sorted(inp_pt):
                return False
        
        # 验证几何结构
        return cls.is_cube(points)
    
    # 其他额外方法

