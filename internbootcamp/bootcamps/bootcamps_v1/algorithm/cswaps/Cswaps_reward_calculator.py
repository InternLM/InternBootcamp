import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from heapq import heapify
from heapq import heappop
from heapq import heappush




class CswapsRewardCalculator(BaseRewardCalculator):
    """Cswaps奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        lines = solution.strip().split('\n')
        expected_possible = identity['possible']
        if not expected_possible:
            return len(lines) >= 1 and lines[0].strip() == "No"
        if len(lines) < 2 or lines[0].strip() != "Yes":
            return False
        try:
            k = int(lines[1].strip())
            if k != identity['s'] // 2 or len(lines) != 2 + k:
                return False
            swaps = [tuple(map(int, line.strip().split())) for line in lines[2:]]
            swap_counts = [0] * identity['n']
            for i, j in swaps:
                if i == j or not (1 <= i <= identity['n']) or not (1 <= j <= identity['n']):
                    return False
                swap_counts[i-1] += 1
                swap_counts[j-1] += 1
            if swap_counts != identity['a']:
                return False
            players = [{i+1: identity['a'][i]} if identity['a'][i] > 0 else {} for i in range(identity['n'])]
            for i, j in swaps:
                if (i not in players[i-1]) or players[i-1][i] < 1 or (j not in players[j-1]) or players[j-1][j] < 1:
                    return False
                players[i-1][i] -= 1
                if players[i-1][i] == 0:
                    del players[i-1][i]
                players[j-1][j] -= 1
                if players[j-1][j] == 0:
                    del players[j-1][j]
                players[i-1][j] = players[i-1].get(j, 0) + 1
                players[j-1][i] = players[j-1].get(i, 0) + 1
            for idx in range(identity['n']):
                if (idx + 1) in players[idx]:
                    return False
            return True
        except:
            return False
    
    # 其他额外方法

