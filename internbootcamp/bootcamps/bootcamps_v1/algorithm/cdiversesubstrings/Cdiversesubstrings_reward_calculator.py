import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict
from collections import deque




class CdiversesubstringsRewardCalculator(BaseRewardCalculator):
    """Cdiversesubstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        numbers = []
        last_answer = matches[-1].strip()
        for line in last_answer.split('\n'):
            line = line.strip()
            if line:
                try:
                    numbers.append(int(line))
                except ValueError:
                    return None
        
        return numbers if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list) or len(solution) != identity['d'] + 1:
            return False
        if solution[0] != identity['d']:
            return False
        return solution[1:] == identity['t_list']
    
    # 其他额外方法

