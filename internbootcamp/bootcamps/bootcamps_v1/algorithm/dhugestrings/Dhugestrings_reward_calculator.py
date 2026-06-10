import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import pow




class DhugestringsRewardCalculator(BaseRewardCalculator):
    """Dhugestrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(.*?)\s*\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_match = matches[-1].strip()
        answers = []
        for line in last_match.split('\n'):
            line = line.strip()
            if line.isdigit():
                answers.append(int(line))
        return answers if len(answers) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('answers', [])
        return isinstance(solution, list) and solution == expected
    
    # 其他额外方法

