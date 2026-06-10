import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import random
import re
import bisect




class ChackerpackyourbagsInstructionGenerator(BaseInstructionGenerator):
    """Chackerpackyourbags Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_x=20, max_duration=200000, max_cost=10**9):
        """
        初始化Chackerpackyourbags指令生成器
        
        Args:
            max_n: 参数描述
            max_x: 参数描述
            max_duration: 参数描述
            max_cost: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_x = max_x
        self.max_duration = max_duration
        self.max_cost = max_cost
    
    def case_generator(self):
        x = random.randint(2, self.max_x)
        vouchers = []
        has_solution = random.choice([True, False])
        
        if has_solution:
            # 确保存在唯一最优解
            duration1 = random.randint(1, x-1)
            duration2 = x - duration1
            attempts = 0
            
            while True:
                # 生成第一个优惠券
                l1 = random.randint(1, self.max_duration - duration1)
                r1 = l1 + duration1 - 1
                
                # 生成第二个优惠券的位置
                if random.choice([True, False]):
                    # 在第一个之后
                    l2_min = r1 + 1
                    r2_max = min(l2_min + duration2 + 3, self.max_duration)
                    if r2_max - l2_min + 1 < duration2:
                        continue
                    l2 = random.randint(l2_min, r2_max - duration2 + 1)
                    r2 = l2 + duration2 - 1
                else:
                    # 在第一个之前
                    r2_max = l1 - 1
                    if r2_max < 1:
                        continue
                    l2_min = max(1, r2_max - duration2 + 1)
                    r2 = random.randint(l2_min + duration2 - 1, r2_max)
                    l2 = r2 - duration2 + 1
                
                # 验证区间有效性
                if (1 <= l2 <= r2 <= self.max_duration and 
                    (r1 < l2 or r2 < l1) and 
                    (r2 - l2 + 1) == duration2):
                    break
                
                attempts += 1
                if attempts > 100:
                    has_solution = False
                    break
            
            if has_solution:
                # 生成最优解对
                c1 = random.randint(1, self.max_cost//4)
                c2 = random.randint(1, self.max_cost//4)
                vouchers = [(l1, r1, c1), (l2, l2 + duration2 - 1, c2)]
                
                # 添加干扰数据
                for _ in range(random.randint(0, self.max_n-2)):
                    while True:
                        l = random.randint(1, self.max_duration)
                        r = random.randint(l, self.max_duration)
                        d = r - l + 1
                        if d + duration1 != x and d + duration2 != x:
                            break
                    cost = random.randint(max(c1, c2)+1, self.max_cost)
                    vouchers.append((l, r, cost))
        
        if not has_solution:
            # 生成无解情况
            base_duration = x + 1
            min_duration = max(1, x//2 + 1)
            for _ in range(random.randint(2, self.max_n)):
                duration = random.randint(min_duration, x + 5)
                l = random.randint(1, self.max_duration - duration)
                r = l + duration - 1
                cost = random.randint(1, self.max_cost)
                vouchers.append((l, r, cost))
        
        random.shuffle(vouchers)
        return {
            'n': len(vouchers),
            'x': x,
            'vouchers': [{'l': l, 'r': r, 'cost': c} for (l, r, c) in vouchers]
        }
    
    @staticmethod
    def prompt_func(question_case):
        voucher_lines = '\n'.join(
            f"{v['l']} {v['r']} {v['cost']}" 
            for v in question_case['vouchers']
        )
        return f"""Select two NON-OVERLAPPING travel vouchers meeting:
1. Sum of durations EXACTLY {question_case['x']} days
2. Minimum total cost

Available vouchers:
{voucher_lines}

Output format: [answer]number[/answer] where number is the minimal cost or -1""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def optimal_solution(vouchers, x):
        duration_map = defaultdict(list)
        for l, r, cost in vouchers:
            duration = r - l + 1
            duration_map[duration].append((l, cost))

        # 预处理每个duration的最小成本
        pre_min = {}
        for d in duration_map:
            sorted_list = sorted(duration_map[d], key=lambda x: x[0])
            min_prefix = []
            current_min = float('inf')
            for l, c in reversed(sorted_list):
                current_min = min(current_min, c)
                min_prefix.append(current_min)
            min_prefix.reverse()
            pre_min[d] = (sorted_list, min_prefix)

        min_cost = float('inf')

        for l, r, cost in vouchers:
            current_duration = r - l + 1
            need_duration = x - current_duration
            if need_duration not in pre_min:
                continue

            sorted_list, min_prefix = pre_min[need_duration]
            idx = bisect.bisect_right(sorted_list, (r, float('inf')))

            if idx < len(min_prefix):
                min_cost = min(min_cost, cost + min_prefix[idx])

        return min_cost if min_cost != float('inf') else -1
