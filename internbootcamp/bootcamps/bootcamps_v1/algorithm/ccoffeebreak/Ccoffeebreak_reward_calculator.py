import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from heapq import heappush
from heapq import heappop
import re
from collections import defaultdict




class CcoffeebreakRewardCalculator(BaseRewardCalculator):
    """Ccoffeebreak奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        lines = [line.strip() for line in answer_block.split('\n') if line.strip()]
        if len(lines) != 2:
            return None
        try:
            k = int(lines[0])
            days = list(map(int, lines[1].split()))
        except:
            return None
        if len(days) == 0:
            return None
        return (k, days)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        user_k, user_days = solution
        a = identity['a']
        n = identity['n']
        d = identity['d']
        m = identity['m']

        tm = sorted(a)
        tail_tm = []
        day_id = {}
        for t in tm:
            if tail_tm and t - tail_tm[0][0] > d:
                existing_day = tail_tm[0][1]
                day_id[t] = existing_day
                heappop(tail_tm)
                heappush(tail_tm, (t, existing_day))
            else:
                new_day = len(tail_tm) + 1
                day_id[t] = new_day
                heappush(tail_tm, (t, new_day))
        k_correct = len(tail_tm)
        days_correct = [day_id[t] for t in a]

        if user_k != k_correct:
            return False

        if len(user_days) != n:
            return False

        if any(day < 1 or day > user_k for day in user_days):
            return False

        day_groups = defaultdict(list)
        for time, day in zip(a, user_days):
            day_groups[day].append(time)

        for times in day_groups.values():
            sorted_times = sorted(times)
            for i in range(1, len(sorted_times)):
                if sorted_times[i] - sorted_times[i-1] < d:
                    return False
        return True
    
    # 其他额外方法

