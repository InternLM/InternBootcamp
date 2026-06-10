import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_candy_boxes(n, s, k, r_list, color_str):
    s -= 1  # 转换为0-based索引
    r = r_list
    color = color_str
    INF = float('inf')
    
    # 预处理最大可能的糖果数
    max_possible = sum(r)
    if max_possible < k:
        return -1
    
    # 动态规划数组，dp[cur][c]表示从cur出发，获得至少c颗糖果的最短时间
    dp = [[INF] * (k + 1) for _ in range(n)]
    
    # 预处理每个盒子自身的情况
    for i in range(n):
        current_max = min(r[i], k)
        for c in range(current_max + 1):
            dp[i][c] = 0  # 只需要吃当前盒子即可
        
    # 记忆化搜索函数
    def dfs(cur):
        # 已经处理过的情况直接返回
        if dp[cur][k] != INF:
            return
        
        # 尝试所有可能的后继盒子
        for to in range(n):
            if color[to] != color[cur] and r[to] > r[cur]:
                dfs(to)
                distance = abs(cur - to)
                
                # 状态转移：当前吃掉的糖果数 + 后续吃掉的糖果数
                for c in range(k, -1, -1):
                    if dp[cur][c] == INF:
                        continue
                    
                    # 计算转移后的糖果数
                    new_c = min(c + r[to], k)
                    cost = dp[cur][c] + distance
                    if cost < dp[to][new_c]:
                        dp[to][new_c] = cost
                        # 回溯更新所有可能的更优解
                        for nc in range(new_c, k+1):
                            if dp[to][nc] > cost:
                                dp[to][nc] = cost
    
    # 从每个可能的起点开始计算
    for i in range(n):
        dfs(i)
    
    # 计算最小时间
    min_time = INF
    for i in range(n):
        start_cost = abs(i - s)
        if start_cost + dp[i][k] < min_time:
            min_time = start_cost + dp[i][k]
    
    return min_time if min_time != INF else -1


class CtanyaandcoloredcandiesRewardCalculator(BaseRewardCalculator):
    """Ctanyaandcoloredcandies奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多种格式的答案提取，包含可能的换行和空格
        matches = re.findall(r'\[answer\s*\]\s*(-?\d+)\s*\[/answer\s*\]', output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1].strip())
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 直接调用求解函数验证答案正确性
            ground_truth = solve_candy_boxes(
                identity['n'],
                identity['s'],
                identity['k'],
                identity['r'],
                identity['colors']
            )
            return solution == ground_truth
        except:
            return False
    
    # 其他额外方法

