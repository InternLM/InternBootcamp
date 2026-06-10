import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
# 无需额外导入

# === 源文件中的全局函数 ===

def compute_max_freq_min_num(n, k, arr):
    arr.sort()
    max_x = 0
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) * arr[right] - current_sum > k:
            current_sum -= arr[left]
            left += 1
        current_x = right - left + 1
        if current_x > max_x:
            max_x = current_x

    min_num = float('inf')
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) > max_x:
            current_sum -= arr[left]
            left += 1
        if (right - left + 1) == max_x:
            cost = max_x * arr[right] - current_sum
            if cost <= k and arr[right] < min_num:
                min_num = arr[right]
    return (max_x, min_num)


class CtoaddornottoaddRewardCalculator(BaseRewardCalculator):
    """Ctoaddornottoadd奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        parts = last_answer.split()
        if len(parts) != 2:
            return None
        try:
            count = int(parts[0])
            number = int(parts[1])
            return (count, number)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        expected_count = identity['max_count']
        expected_number = identity['correct_number']
        return solution[0] == expected_count and solution[1] == expected_number
    
    # 其他额外方法

