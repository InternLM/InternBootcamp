import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import List
from typing import Optional




class AquariumRewardCalculator(BaseRewardCalculator):
    """Aquarium奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[List[int]]:
        # Find all answer blocks
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        # Take the last match
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: List[int], identity: Dict) -> bool:
        cols = len(identity['col_clues'])
        rows = len(identity['row_clues'])
        # Check solution length matches columns
        if len(solution) != cols:
            return False
        # Check each column's solution matches column clue
        for c in range(cols):
            if solution[c] + 1 != identity['col_clues'][c]:
                return False
        # Check each row's filled count matches row clue
        for r in range(rows):
            expected = identity['row_clues'][r]
            actual = sum(1 for c in range(cols) if solution[c] >= r)
            if actual != expected:
                return False
        return True
    
    # 其他额外方法

