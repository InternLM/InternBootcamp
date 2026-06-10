import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import heapq




class DstringRewardCalculator(BaseRewardCalculator):
    """Dstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        return output[start+8:end].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        k = identity['k']
        n = len(s)
        total = n * (n + 1) // 2
        if k > total:
            return solution == "No such line."
        heap = []
        for i in range(len(s)):
            heapq.heappush(heap, (s[i], i))
        current = None
        for _ in range(k):
            current = heapq.heappop(heap)
            if current[1] < len(s) - 1:
                next_char = s[current[1] + 1]
                heapq.heappush(heap, (current[0] + next_char, current[1] + 1))
        expected = current[0] if k <= total else "No such line."
        return solution == expected
    
    # 其他额外方法

