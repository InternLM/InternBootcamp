import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import random
import re




class CarthurandtableInstructionGenerator(BaseInstructionGenerator):
    """Carthurandtable Bootcamp指令生成器"""
    
    def __init__(self, max_legs=20, max_length=100, max_energy=200):
        """
        初始化Carthurandtable指令生成器
        
        Args:
            max_legs: 参数描述
            max_length: 参数描述
            max_energy: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_legs = max_legs
        self.max_length = max_length
        self.max_energy = max_energy
    
    def case_generator(self):
        n = random.randint(1, self.max_legs)
        
        # 生成多维度案例
        max_length = random.randint(1, self.max_length)
        candidates = [
            lambda: random.randint(1, max_length-1) if max_length>1 else 1,
            lambda: max_length
        ]
        
        # 确保存在有效最长腿
        main_count = random.randint(1, n)
        legs = [max_length] * main_count
        
        # 生成其他腿（允许存在与最长腿相同的情况）
        for _ in range(n - main_count):
            legs.append(random.choice(candidates)())
        
        random.shuffle(legs)
        di = [random.randint(1, self.max_energy) for _ in range(n)]
        return {"n": n, "l": legs, "d": di}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        l = ' '.join(map(str, question_case['l']))
        d = ' '.join(map(str, question_case['d']))
        return f"""Arthur需要稳定桌子。桌子有{n}条腿：
长度：{l}
移除能耗：{d}

稳定条件：
1. 剩余k条腿中，最大长度的腿数量 > k/2
2. 单腿总是稳定，双腿需等长

请计算最小能耗，答案放在[ANSWER]标签内。示例：[ANSWER]42[/ANSWER]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_energy(n, l, d):
        leg_info = sorted(zip(l, d), key=lambda x: -x[1])
        freq = defaultdict(int)
        cost_map = defaultdict(list)

        for li, di in zip(l, d):
            freq[li] += 1
            cost_map[li].append(di)

        total_cost = sum(d)
        min_energy = float('inf')

        for length in freq:
            current_cost = total_cost - sum(cost_map[length])
            available = freq[length] - 1

            # 计算必须移除的长腿
            longer_cost = sum(di for li, di in zip(l, d) if li > length)

            # 处理需要移除的短腿
            short_legs = sorted([di for li, di in zip(l, d) if li < length], reverse=True)
            keep = min(available, len(short_legs))
            current_cost -= sum(short_legs[:keep])

            # 最终总能耗
            final_cost = longer_cost + (sum(short_legs) - sum(short_legs[:keep]))
            min_energy = min(min_energy, final_cost)

        return min_energy
