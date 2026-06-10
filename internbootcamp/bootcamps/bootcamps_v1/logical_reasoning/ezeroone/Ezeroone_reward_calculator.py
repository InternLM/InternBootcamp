import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EzerooneRewardCalculator(BaseRewardCalculator):
    """Ezeroone奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.search(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        content = match.group(1).strip()
        lines = content.split('\n')
        results = []
        for line in lines:
            line = line.strip()
            if len(line) == 2 and line.isdigit():
                results.append(line)
        if not results:
            return None
        results = sorted(results)
        return results
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        initial = identity['initial']
        expected = Ezeroonebootcamp.compute_possible_outcomes(initial)
        return solution == expected
    
    # 其他额外方法

