import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import heapq
from heapq import heappush
from heapq import heappop
import random

# === 源文件中的全局函数 ===

def calculate_max_pleasure(n, m, k, p, matrix):
    # 计算初始行和列的总和
    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(n)) for j in range(m)]

    # 初始化最大堆（使用负数实现最小堆模拟最大堆）
    row_heap = [-s for s in row_sums]
    heapq.heapify(row_heap)
    col_heap = [-s for s in col_sums]
    heapq.heapify(col_heap)

    # 预计算所有可能的行操作收益
    pr = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not row_heap:
            break
        current = -heappop(row_heap)
        current_sum += current
        pr[h] = current_sum
        heappush(row_heap, -(current - m*p))  # 更新行总和

    # 预计算所有可能的列操作收益
    pc = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not col_heap:
            break
        current = -heappop(col_heap)
        current_sum += current
        pc[h] = current_sum
        heappush(col_heap, -(current - n*p))  # 更新列总和

    # 穷举所有可能的行、列操作组合
    max_total = -float('inf')
    for i in pr:
        j = k - i
        if j >= 0 and j in pc:
            total = pr[i] + pc[j] - i*j*p
            max_total = max(max_total, total)
    
    return max_total if max_total != -float('inf') else 0


class BdzylovesmodificationRewardCalculator(BaseRewardCalculator):
    """Bdzylovesmodification奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

