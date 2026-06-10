import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from typing import List
from typing import Tuple
from typing import Union




class DcuptrickRewardCalculator(BaseRewardCalculator):
    """Dcuptrick奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Union[List[int], int, None]:
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return -1
        try:
            solution = list(map(int, last_match.split()))
            if all(1 <= num <= 1000000 for num in solution):
                return solution
            else:
                return None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        expected = identity['expected_solution']
        if expected == -1:
            return solution == -1
        else:
            return solution == expected
    
    # 其他额外方法

