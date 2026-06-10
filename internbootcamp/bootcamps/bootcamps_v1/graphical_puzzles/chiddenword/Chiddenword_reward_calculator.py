import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import string
import random




class ChiddenwordRewardCalculator(BaseRewardCalculator):
    """Chiddenword奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = re.compile(r'\[answer\](.*?)\[\/answer\]', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if 'impossible' in last_match.lower():
            return 'Impossible'
        rows = [line.strip() for line in last_match.split('\n') if line.strip()]
        if len(rows) == 2 and len(rows[0]) == 13 and len(rows[1]) == 13 and rows[0].isupper() and rows[1].isupper():
            return rows
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_output']
        if expected == "Impossible":
            return solution == "Impossible"
        else:
            return solution == expected
    
    # 其他额外方法

