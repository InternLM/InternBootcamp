import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ElittleelephantandshiftsRewardCalculator(BaseRewardCalculator):
    """Elittleelephantandshifts奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extracts the solution from the model's output, expecting the last [answer] block.
        Returns a list of integers or None if extraction fails.
        """
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        solution = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                try:
                    solution.append(int(line))
                except ValueError:
                    return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        Verifies if the extracted solution matches the precomputed correct outputs.
        """
        correct_outputs = identity.get('correct_outputs', [])
        return solution == correct_outputs if solution is not None else False
    
    # 其他额外方法

