import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class DthewuRewardCalculator(BaseRewardCalculator):
    """Dthewu奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        w = identity['w']
        s_multiset = identity['s_multiset']
        t_str = identity['t']
        k = identity['k']
        
        t_int = int(t_str, 2)
        correct = 0
        
        for s_str, count in s_multiset.items():
            s_int = int(s_str, 2)
            xor = s_int ^ t_int
            wu = sum(w[n - i - 1] for i in range(n) if (xor & (1 << i)) == 0)
            
            if wu <= k:
                correct += count
        
        return solution == correct
    
    # 其他额外方法

