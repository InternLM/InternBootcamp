import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import accumulate




class CgreedyshoppingRewardCalculator(BaseRewardCalculator):
    """Cgreedyshopping奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answers = []
        for line in matches[-1].strip().split('\n'):
            if line.strip().isdigit():
                answers.append(int(line.strip()))
        return answers or None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answers']
    
    # 其他额外方法

