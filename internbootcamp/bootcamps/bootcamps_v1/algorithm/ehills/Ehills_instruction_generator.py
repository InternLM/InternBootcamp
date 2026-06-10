import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EhillsInstructionGenerator(BaseInstructionGenerator):
    """Ehills Bootcamp指令生成器"""
    
    def __init__(self, max_n: int = 10, max_height: int = 100):
        """
        初始化Ehills指令生成器
        
        Args:
            max_n: 参数描述
            max_height: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_height = max_height
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        heights = [random.randint(1, self.max_height) for _ in range(n)]
        expected_output = compute_min_time(n, heights)
        return {
            "n": n,
            "heights": heights,
            "expected_output": expected_output
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = (
            "Innopolis city needs to adjust hills for building houses. Each hill must be strictly taller than neighbors.\n"
            f"Given {question_case['n']} hills with heights: {', '.join(map(str, question_case['heights']))}.\n"
            f"Calculate the minimum time (hours) needed for each k from 1 to {math.ceil(question_case['n']/2)}. "
            "Output space-separated integers enclosed in [answer]...[/answer].\n"
            "Example Answer Format: [answer]0 1 3[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

