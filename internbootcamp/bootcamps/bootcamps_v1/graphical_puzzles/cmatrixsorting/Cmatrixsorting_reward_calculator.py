import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from copy import deepcopy
from typing import List
from typing import Union




class CmatrixsortingRewardCalculator(BaseRewardCalculator):
    """Cmatrixsorting奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Union[List[int], int, None]:
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        
        if last_match == '-1':
            return -1
        if last_match == '0':
            return []
        
        try:
            return list(map(int, last_match.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):        
        A = identity['A']
        B = identity['B']
        m = identity['m']
        has_solution = identity['has_solution']

        if not has_solution:
            return solution == -1
        
        if solution == -1:
            return False
        
        if solution == []:
            return A == B
        
        if any(not 1 <= c <= m for c in solution):
            return False

        sorted_table = deepcopy(A)
        for col in solution:
            sorted_table.sort(key=lambda row: row[col-1])
        return sorted_table == B
    
    # 其他额外方法

