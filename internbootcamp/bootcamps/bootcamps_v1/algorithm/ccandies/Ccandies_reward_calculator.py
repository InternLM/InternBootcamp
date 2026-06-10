import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CcandiesRewardCalculator(BaseRewardCalculator):
    """Ccandies奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        last_answer = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not last_answer:
            return None
        answers = []
        for line in last_answer[-1].strip().splitlines():
            cleaned = line.strip()
            if cleaned.isdigit():
                answers.append(int(cleaned))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != len(identity['queries']):
            return False
        s = identity['s']
        for i, query in enumerate(identity['queries']):
            l, r = query['l'], query['r']
            expected = cls.compute_f(s[l-1:r])
            if solution[i] != expected:
                return False
        return True
    
    # 其他额外方法

