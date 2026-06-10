import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
from collections import deque




class BintersectingsubtreesRewardCalculator(BaseRewardCalculator):
    """Bintersectingsubtrees奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches: return None
        try: return int(matches[-1].strip())
        except: return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        x_set = set(case['x_list'])
        y_set = set(case['y_list'])
        perm = case['permutation']
        
        # 验证solution格式
        if solution == -1:
            return all(perm[x-1] not in y_set for x in x_set)
        else:
            return solution in x_set and perm[solution-1] in y_set
    
    # 其他额外方法

