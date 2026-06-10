import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ChistoryRewardCalculator(BaseRewardCalculator):
    """Chistory奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        events = identity['events']
        if n == 0:
            return solution == 0
        sorted_events = sorted(events, key=lambda x: x[0])
        max_end = sorted_events[0][1]
        cnt = 0
        for i in range(1, n):
            current_end = sorted_events[i][1]
            if current_end > max_end:
                max_end = current_end
            else:
                cnt += 1
        return solution == cnt
    
    # 其他额外方法

