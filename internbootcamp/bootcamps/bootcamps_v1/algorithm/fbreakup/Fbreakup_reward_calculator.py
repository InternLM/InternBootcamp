import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque




class FbreakupRewardCalculator(BaseRewardCalculator):
    """Fbreakup奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        
        lines = [l.strip() for l in last_answer.split('\n') if l.strip()]
        if len(lines) < 2:
            return None
        
        try:
            # 处理无解情况
            if lines[0] == '-1':
                return {'min_budget': -1, 'c': 0, 'roads': []}
            
            # 解析正常情况
            total_cost = int(lines[0])
            road_count = int(lines[1])
            if road_count == 0:
                return {'min_budget': total_cost, 'c': 0, 'roads': []}
            
            if len(lines) < 3:
                return None
            road_indices = list(map(int, lines[2].split()))
            if len(road_indices) != road_count or road_count not in (1,2):
                return None
            
            return {
                'min_budget': total_cost,
                'c': road_count,
                'roads': road_indices
            }
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理无解情况
        if identity['expected'] == -1:
            return solution.get('min_budget') == -1
        
        # 验证数值正确性
        expected = identity['expected']
        if (solution['min_budget'] != expected['min_budget'] or
            solution['c'] != expected['c']):
            return False
        
        # 验证边集合是否匹配（顺序无关）
        if set(solution['roads']) != set(expected['roads']):
            return False
        
        # 验证图是否真正断开
        return cls._is_disconnected(
            identity['n'], 
            identity['roads'],
            identity['s'],
            identity['t'],
            solution['roads']
        )
    
    # 其他额外方法

