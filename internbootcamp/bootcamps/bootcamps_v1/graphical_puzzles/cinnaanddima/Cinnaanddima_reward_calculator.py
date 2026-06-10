import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any




class CinnaanddimaRewardCalculator(BaseRewardCalculator):
    """Cinnaanddima奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if matches:
            return matches[-1].strip()
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict[str, Any]) -> bool:
        grid = identity['grid']
        n = identity['n']
        m = identity['m']
        correct_ans = cls._compute_correct_answer(grid, n, m)
        return solution == correct_ans
    
    # 其他额外方法

