import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CzerooneRewardCalculator(BaseRewardCalculator):
    """Czeroone奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n')]
        valid = []
        for line in lines:
            if line in {'00', '01', '10', '11'}:
                valid.append(line)
        return valid if valid else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):  # 修正缩进
        if not solution:
            return False
        expected = cls.compute_valid_outcomes(identity['input'])
        return sorted(solution) == sorted(expected)
    
    # 其他额外方法

