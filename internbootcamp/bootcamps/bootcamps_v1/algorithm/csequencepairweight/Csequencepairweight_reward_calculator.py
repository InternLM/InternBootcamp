import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
from random import randint
import re




class CsequencepairweightRewardCalculator(BaseRewardCalculator):
    """Csequencepairweight奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n')]
        lines = [line for line in lines if line]
        try:
            solution = list(map(int, lines))
        except:
            return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        expected = [case['output'] for case in identity['cases']]
        return solution == expected
    
    # 其他额外方法

