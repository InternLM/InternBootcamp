import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from functools import lru_cache
import re




class EdoegraphsRewardCalculator(BaseRewardCalculator):
    """Edoegraphs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        answers = []
        for line in answer_block.split('\n'):
            line = line.strip()
            if line:
                if line.isdigit() or (line.startswith('-') and line[1:].isdigit()):
                    answers.append(int(line))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        n = identity['n']
        queries = identity['queries']
        if len(solution) != len(queries):
            return False
        for (a, b), user_ans in zip(queries, solution):
            correct_ans = cls.compute_shortest_path(a, b, n)
            if user_ans != correct_ans:
                return False
        return True
    
    # 其他额外方法

