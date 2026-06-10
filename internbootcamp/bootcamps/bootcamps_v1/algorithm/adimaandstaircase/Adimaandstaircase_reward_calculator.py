import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class AdimaandstaircaseRewardCalculator(BaseRewardCalculator):
    """Adimaandstaircase奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        numbers = []
        for line in last_match.split('\n'):
            stripped = line.strip()
            if stripped:
                try:
                    numbers.append(int(stripped))
                except ValueError:
                    continue
        return numbers if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        boxes = identity['boxes']
        correct = []
        current_l = 0
        previous_h = 0
        for w, h in boxes:
            current_l = max(current_l + previous_h, a[w-1])
            correct.append(current_l)
            previous_h = h
        return solution == correct
    
    # 其他额外方法

