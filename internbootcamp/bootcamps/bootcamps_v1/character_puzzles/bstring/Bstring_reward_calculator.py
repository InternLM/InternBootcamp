import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from heapq import heappush
from heapq import heappop
from heapq import heapify




class BstringRewardCalculator(BaseRewardCalculator):
    """Bstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        k = identity['k']
        
        # Edge case: k exceeds maximum possible
        total = len(s) * (len(s)+1) // 2
        if k > total or k > identity.get('max_k', 10**5):
            return solution == "No such line."
        
        # Heap-based k-th smallest calculation
        heap = [(s[i], i) for i in range(len(s))]
        heapify(heap)
        
        result = None
        for _ in range(k):
            curr, pos = heappop(heap)
            result = curr
            if pos + 1 < len(s):
                heappush(heap, (curr + s[pos+1], pos+1))
        
        return solution == result
    
    # 其他额外方法

