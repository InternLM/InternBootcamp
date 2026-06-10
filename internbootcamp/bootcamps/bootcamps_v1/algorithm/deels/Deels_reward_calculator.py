import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import random
from collections import defaultdict
import re




class DeelsRewardCalculator(BaseRewardCalculator):
    """Deels奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        solution = []
        for line in last_answer.splitlines():
            line = line.strip()
            if line:
                try:
                    solution.append(int(line))
                except ValueError:
                    pass
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answers']
    
    # 其他额外方法

