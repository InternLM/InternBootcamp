import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EsubsetsumsRewardCalculator(BaseRewardCalculator):
    """Esubsetsums奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_answer = matches[-1].strip()
        answers = []
        for line in last_answer.split('\n'):
            clean_line = line.strip()
            if clean_line:
                if re.match(r'^-?\d+$', clean_line):
                    answers.append(int(clean_line))
                elif re.match(r'^-?\d+\.\d+$', clean_line):
                    answers.append(int(float(clean_line)))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('correct_outputs', [])
    
    # 其他额外方法

