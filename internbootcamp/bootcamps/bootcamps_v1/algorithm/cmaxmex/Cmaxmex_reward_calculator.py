import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CmaxmexRewardCalculator(BaseRewardCalculator):
    """Cmaxmex奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        answers = []
        for line in last_match.split('\n'):
            stripped = line.strip()
            if stripped:
                answers.append(stripped)
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct_answers = [q['answer'] for q in identity['queries'] if q['type'] == 2]
        if not solution or len(solution) != len(correct_answers):
            return False
        try:
            user_answers = list(map(int, solution))
            return user_answers == correct_answers
        except ValueError:
            return False
    
    # 其他额外方法

