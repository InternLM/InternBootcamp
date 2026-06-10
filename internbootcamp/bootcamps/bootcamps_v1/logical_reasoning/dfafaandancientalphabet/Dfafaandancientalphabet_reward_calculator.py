import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DfafaandancientalphabetRewardCalculator(BaseRewardCalculator):
    """Dfafaandancientalphabet奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the last occurrence of an answer enclosed in [answer] tags.
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        Verify if the extracted solution matches the correct answer.
        """
        correct_answer = cls.calculate_correct_answer(
            identity['n'],
            identity['m'],
            identity['A'],
            identity['B']
        )
        return solution == correct_answer
    
    # 其他额外方法

