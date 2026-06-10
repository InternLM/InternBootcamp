import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DvasyaandchessRewardCalculator(BaseRewardCalculator):
    """Dvasyaandchess奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        solution = solution.strip()
        lines = [line.strip() for line in solution.split('\n') if line.strip()]

        if n % 2 == 0:
            return (len(lines) == 2 and 
                    lines[0].lower() == 'white' and 
                    list(map(int, lines[1].split())) == [1, 2])
        else:
            return len(lines) == 1 and lines[0].lower() == 'black'
    
    # 其他额外方法

