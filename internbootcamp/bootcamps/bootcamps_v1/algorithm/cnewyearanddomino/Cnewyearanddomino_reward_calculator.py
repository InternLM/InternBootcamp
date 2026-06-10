import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CnewyearanddominoRewardCalculator(BaseRewardCalculator):
    """Cnewyearanddomino奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return list(map(int, matches[-1].strip().split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list) or len(solution) != len(identity['correct_answers']):
            return False
        return all(s == a for s, a in zip(solution, identity['correct_answers']))
    
    # 其他额外方法

