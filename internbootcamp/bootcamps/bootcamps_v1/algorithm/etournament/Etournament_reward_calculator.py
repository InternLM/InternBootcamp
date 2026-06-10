import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import random
from typing import List
from typing import Optional

# === 源文件中的其他类 ===

class Node:
    def __init__(self, s_list):
        self.mx = s_list.copy()
        self.mn = s_list.copy()
        self.sz = 1
    
    def __lt__(self, other: 'Node') -> bool:
        for i in range(len(self.mn)):
            if self.mn[i] < other.mx[i]:
                return True
        return False
    
    def is_greater_than(self, other: 'Node') -> bool:
        for i in range(len(self.mx)):
            if self.mx[i] > other.mn[i]:
                return True
        return False


class EtournamentRewardCalculator(BaseRewardCalculator):
    """Etournament奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[List[int]]:
        start_tag = '[answer]'
        end_tag = '[/answer]'
        start_idx = output.rfind(start_tag)
        end_idx = output.rfind(end_tag)
        
        if start_idx == -1 or end_idx == -1:
            return None
        
        answer_lines = output[start_idx+len(start_tag):end_idx].strip().split('\n')
        try:
            return [int(line.strip()) for line in answer_lines if line.strip()]
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        return solution == identity['correct_output']
    
    # 其他额外方法

