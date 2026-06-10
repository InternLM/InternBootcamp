import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CinnaandcandyboxesRewardCalculator(BaseRewardCalculator):
    """Cinnaandcandyboxes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        last_answer = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not last_answer:
            return None
        answers = []
        for line in last_answer[-1].strip().splitlines():
            if line.strip().isdigit():
                answers.append(int(line.strip()))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != identity['w']:
            return False
        try:
            correct = cls.solve_case(
                identity['n'], identity['k'], identity['w'],
                identity['s'], identity['queries']
            )
            return solution == correct
        except:
            return False
    
    # 其他额外方法

