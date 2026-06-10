import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CboboniuandstringRewardCalculator(BaseRewardCalculator):
    """Cboboniuandstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        distance_line = lines[0]
        t_line = lines[1]
        if not t_line or any(c not in {'B', 'N'} for c in t_line):
            return None
        try:
            user_distance = int(distance_line)
        except ValueError:
            return None
        return f"{user_distance}\n{t_line}"
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        parts = solution.split('\n')
        if len(parts) < 2:
            return False
        
        try:
            user_distance = int(parts[0])
            user_t = parts[1]
        except:
            return False
        
        # Check valid non-empty string
        x_user = user_t.count('N')
        y_user = user_t.count('B')
        if x_user + y_user == 0:
            return False
        
        # Re-calculate actual distance for user's solution
        max_distance = 0
        for a, b in zip(identity['a_list'], identity['b_list']):
            if x_user == 0 and y_user == 0:
                return False  # Already checked above
            
            if x_user <= a and y_user <= b:
                current = max(a - x_user, b - y_user)
            elif x_user <= a or y_user <= b:
                current = abs(a - x_user) + abs(b - y_user)
            else:
                current = max(x_user - a, y_user - b)
            
            if current > max_distance:
                max_distance = current
        
        # Validate two conditions:
        # 1. User's reported distance matches actual calculated distance
        # 2. The distance matches the optimal solution
        return user_distance == max_distance and max_distance == identity['max_distance']
    
    # 其他额外方法

