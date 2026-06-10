import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_max_median(n, k, array):
    """优化后的中位数计算函数"""
    left, right = min(array), max(array)
    answer = left  # 初始化
    
    while left <= right:
        mid = (left + right) // 2
        prefix = [0]*(n+1)
        min_prefix = float('inf')
        
        # 计算前缀和
        for i in range(n):
            prefix[i+1] = prefix[i] + (1 if array[i] >= mid else -1)
        
        # 寻找有效窗口
        valid = False
        for i in range(k, n+1):
            if prefix[i] - min_prefix > 0:
                valid = True
                break
            min_prefix = min(min_prefix, prefix[i - k + 1])
        
        if valid:
            answer = mid
            left = mid + 1
        else:
            right = mid - 1
    
    return answer


class DmaxmedianRewardCalculator(BaseRewardCalculator):
    """Dmaxmedian奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        try:
            return int(matches[-1]) if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

