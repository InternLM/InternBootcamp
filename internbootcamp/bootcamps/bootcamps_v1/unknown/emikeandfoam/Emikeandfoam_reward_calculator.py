import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
from collections import defaultdict




class EmikeandfoamRewardCalculator(BaseRewardCalculator):
    """Emikeandfoam奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answers = []
        for line in matches[-1].strip().split('\n'):
            if line.strip().isdigit():
                answers.append(int(line.strip()))
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = cls._compute_expected(
            identity['n'], identity['q'], 
            identity['a'], identity['queries']
        )
        return solution == expected
    
    # 其他额外方法

