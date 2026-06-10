import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import re
import random
from math import gcd




class CroundcorridorRewardCalculator(BaseRewardCalculator):
    """Croundcorridor奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        answers = []
        for part in last_match.split():
            normalized = part.upper()
            if normalized in ('YES', 'NO'):
                answers.append(normalized)
        return ' '.join(answers) if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        solution_answers = solution.split()
        expected_answers = [q['answer'] for q in identity['queries']]
        if len(solution_answers) != len(expected_answers):
            return False
        for sol, exp in zip(solution_answers, expected_answers):
            if sol != exp.upper():
                return False
        return True
    
    # 其他额外方法

