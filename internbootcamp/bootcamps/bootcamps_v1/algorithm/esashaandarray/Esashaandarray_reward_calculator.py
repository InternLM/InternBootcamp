import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EsashaandarrayRewardCalculator(BaseRewardCalculator):
    """Esashaandarray奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        solution = []
        for line in last_match.split('\n'):
            stripped = line.strip()
            if stripped:
                try:
                    solution.append(int(stripped))
                except:
                    pass
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('expected_outputs', [])
        return solution == expected
    
    # 其他额外方法

