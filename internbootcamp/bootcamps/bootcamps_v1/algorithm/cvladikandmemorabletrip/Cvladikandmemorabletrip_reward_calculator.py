import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_max_comfort(n, a):
    # 预处理每个城市的最左和最右出现位置
    lmost = {}
    rmost = {}
    for i in range(n):
        city = a[i]
        if city not in lmost:
            lmost[city] = i
        rmost[city] = i
    
    dp = [0] * (n + 1)
    
    for i in range(n):
        dp[i+1] = dp[i]  # 默认不选当前段
        
        segment_cities = set()
        current_xor = 0
        min_l = n  # 当前段最小左边界
        valid = True
        
        # 从i往左扫描
        for j in range(i, -1, -1):
            city = a[j]
            
            # 检查该城市是否违反右边界约束
            if rmost.get(city, -1) > i:
                valid = False
                break
            
            # 更新当前段最小左边界
            min_l = min(min_l, lmost[city])
            
            # 仅当j到达当前段理论最小左边界时进行状态转移
            if j == min_l and valid:
                # 计算当前段的XOR
                if city not in segment_cities:
                    segment_cities.add(city)
                    current_xor ^= city
                
                # 状态转移
                dp[i+1] = max(dp[i+1], dp[j] + current_xor)
    
    return dp[n]


class CvladikandmemorabletripRewardCalculator(BaseRewardCalculator):
    """Cvladikandmemorabletrip奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

