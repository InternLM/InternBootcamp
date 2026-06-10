import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class DteamsformationRewardCalculator(BaseRewardCalculator):
    """Dteamsformation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            ans = int(solution)
        except:
            return False
        
        n, k, m = identity['n'], identity['k'], identity['m']
        a = identity['a']
        
        # 压缩原始序列
        stack = []
        for city in a:
            if stack and stack[-1][0] == city:
                stack[-1] = (city, stack[-1][1] + 1)
                if stack[-1][1] == k:
                    stack.pop()
            else:
                stack.append((city, 1))
        if not stack:
            return ans == 0
        
        # 处理多趟次合并
        q = deque(stack)
        cycle_len = len(q)
        total_cycles = m
        removed = 0
        
        # 首尾合并处理
        while len(q) >= 2 and q[0][0] == q[-1][0]:
            front_city, front_cnt = q[0]
            back_city, back_cnt = q[-1]
            
            total = front_cnt + back_cnt
            if total < k:
                break
                
            if total % k == 0:
                removed += total * (total_cycles - 1)
                q.popleft()
                q.pop()
                total_cycles = 1  # 剩余部分只能处理一次
            else:
                new_cnt = total % k
                removed += (total - new_cnt) * (total_cycles - 1)
                q[0] = (front_city, new_cnt)
                q.pop()
                total_cycles = 1
                break
        
        # 计算最终结果
        if len(q) == 0:
            final = 0
        elif len(q) == 1:
            total = q[0][1] * total_cycles
            remainder = total % k
            final = remainder + removed
            final = final if remainder != 0 else removed
        else:
            base_sum = sum(cnt for city, cnt in q)
            final = base_sum * total_cycles + removed
        
        return ans == final
    
    # 其他额外方法

