import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CmemoryanddeevolutionRewardCalculator(BaseRewardCalculator):
    """Cmemoryanddeevolution奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 交换x和y以适配参考代码逻辑
        original_x = identity['x']
        original_y = identity['y']
        x = original_y  # 参考代码中的输入xy是颠倒的
        y = original_x
        
        current = [x, x, x]
        goal = [y, y, y]
        steps = 0
        
        while current != goal:
            best_index = -1
            best_value = -1
            for i in range(3):
                a = current[i]
                b = current[(i+1) % 3]
                c = current[(i+2) % 3]
                new_val = min(y, b + c - 1)
                if new_val > a and new_val > best_value:
                    best_index = i
                    best_value = new_val
            
            if best_index == -1:  # 无解
                return False
            
            current[best_index] = best_value
            steps += 1
            
            # 安全阀防止无限循环
            if steps > 1000:
                return False
        
        return solution == steps
    
    # 其他额外方法

