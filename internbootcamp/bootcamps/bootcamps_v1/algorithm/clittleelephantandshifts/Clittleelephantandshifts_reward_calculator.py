import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from heapq import heappop
from heapq import heappush




class ClittleelephantandshiftsRewardCalculator(BaseRewardCalculator):
    """Clittleelephantandshifts奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        try:
            solution = list(map(int, lines))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_output']
        if not isinstance(solution, list) or len(solution) != len(expected):
            return False
        return all(s == e for s, e in zip(solution, expected))
    
    # 其他额外方法

