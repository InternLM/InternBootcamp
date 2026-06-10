import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
from typing import List

# === 源文件中的全局函数 ===

def compute_min_time(n: int, a_list: List[int]) -> List[int]:
    INF = float('inf')
    high = [-INF] + a_list.copy() + [-INF]
    m = math.ceil(n / 2)
    
    # 初始化DP表，使用二维列表表示当前j和状态0/1/2的最小时间
    dp = [[INF] * 3 for _ in range(m + 1)]
    dp[0][0] = 0  # 初始状态：0个峰，最后状态是0（未选）
    
    for i in range(1, n + 1):
        new_dp = [[INF] * 3 for _ in range(m + 1)]
        for j in range(m + 1):
            for state in range(3):
                if dp[j][state] == INF:
                    continue
                
                if state == 0:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，转移到状态1
                    if j < m:
                        cost = 0
                        if high[i] <= high[i - 1]:
                            cost += high[i - 1] - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
                
                elif state == 1:
                    # 当前必须不选i（连续不能选），转移到状态2
                    new_dp[j][2] = min(new_dp[j][2], dp[j][state])
                
                elif state == 2:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，需考虑前前一个峰的影响
                    if j < m:
                        cost = 0
                        prev_peak_height = high[i - 1]
                        # 考虑i-2的影响
                        if i >= 2 and high[i - 2] <= prev_peak_height:
                            prev_peak_height = high[i - 2] - 1
                        # 计算当前i需要调整的高度
                        if high[i] <= prev_peak_height:
                            cost += prev_peak_height - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
        dp = new_dp
    
    # 收集结果
    result = []
    for k in range(1, m + 1):
        min_val = min(dp[k][0], dp[k][1], dp[k][2])
        result.append(min_val if min_val != INF else 0)
    return result


class EhillsRewardCalculator(BaseRewardCalculator):
    """Ehills奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> List[int]:
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        try:
            return list(map(int, last_answer.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: List[int], identity: dict) -> bool:
        return solution == identity['expected_output']
    
    # 其他额外方法

