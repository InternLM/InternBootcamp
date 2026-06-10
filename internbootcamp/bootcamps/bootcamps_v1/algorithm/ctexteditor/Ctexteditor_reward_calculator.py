import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CtexteditorRewardCalculator(BaseRewardCalculator):
    """Ctexteditor奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        patterns = [
            r'\[answer\](.*?)\[\/answer\]',
            r'最少需要[：: ]*(\d+)次按键',
            r'final answer:? (\d+)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, output, re.DOTALL|re.IGNORECASE)
            if matches:
                return matches[-1].strip()
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def min_steps_calculation(params):
            n = params['n']
            a = [x+1 for x in params['a']]
            r1, c1 = params['r1']-1, params['c1']
            r2, c2 = params['r2']-1, params['c2']
            
            min_table = [[float('inf')]*n for _ in range(n)]
            for i in range(n):
                current_min = a[i]
                min_table[i][i] = current_min
                for j in range(i+1, n):
                    current_min = min(current_min, a[j])
                    min_table[i][j] = current_min
                    min_table[j][i] = current_min
            
            min_operations = float('inf')
            for mid in range(n):
                up_min = min_table[mid][r1] if mid <= r1 else min_table[r1][mid]
                col_limit = min(c1, up_min)
                
                down_min = min_table[mid][r2] if mid <= r2 else min_table[r2][mid]
                final_col = min(col_limit, down_min)
                
                vertical = abs(mid - r1) + abs(mid - r2)
                horizontal = abs(final_col - c2)
                total = vertical + horizontal
                
                if total < min_operations:
                    min_operations = total
            
            return min_operations

        try:
            expected = min_steps_calculation(identity)
            return int(solution) == expected
        except (ValueError, KeyError, TypeError):
            return False
    
    # 其他额外方法

