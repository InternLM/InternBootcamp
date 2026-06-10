import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import bisect




class FteodorisnotaliarRewardCalculator(BaseRewardCalculator):
    """Fteodorisnotaliar奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the last occurrence of an answer within [answer] tags.
        """
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        Verify if the extracted solution matches the correct maximum value.
        """
        # Helper function to compute the LIS-based solution
        def solve(v):
            max_size = len(v) + 2
            nums = [float('inf')] * max_size
            nums[0] = 0  # Initial setup as per reference C++ code
            anss = []
            for num in v:
                idx = bisect.bisect_right(nums, num)  # Find first index where nums[idx] > num
                anss.append(idx)
                if idx < len(nums) and nums[idx] > num:
                    nums[idx] = num
            return anss

        # Reconstruct the coverage array
        m = identity['m']
        segments = identity['segments']
        v_diff = [0] * (m + 1)
        for li, ri in segments:
            v_diff[li - 1] += 1
            v_diff[ri] -= 1

        # Compute the actual coverage counts
        v = []
        current = 0
        for i in range(m):
            current += v_diff[i]
            v.append(current)

        # Compute ls and rs arrays
        ls = solve(v)
        reversed_v = v[::-1]
        rs_reversed = solve(reversed_v)
        rs = rs_reversed[::-1]

        # Calculate maximum possible answer
        max_answer = 0
        for i in range(len(v)):
            current_val = ls[i] + rs[i] - 1
            if current_val > max_answer:
                max_answer = current_val

        return solution == max_answer
    
    # 其他额外方法

