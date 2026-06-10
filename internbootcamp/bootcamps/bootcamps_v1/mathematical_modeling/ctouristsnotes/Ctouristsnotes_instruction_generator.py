import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtouristsnotesInstructionGenerator(BaseInstructionGenerator):
    """Ctouristsnotes Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, min_m=1, max_m=5, invalid_prob=0.3):
        """
        初始化Ctouristsnotes指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            invalid_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.invalid_prob = invalid_prob
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        m = random.randint(self.min_m, min(self.max_m, n))
        days = sorted(random.sample(range(1, n + 1), m))
        generate_invalid = random.random() < self.invalid_prob and m >= 2
        notes = []
        h = random.randint(0, 10)
        notes.append((days[0], h))
        conflict_pos = random.randint(0, m - 2) if generate_invalid and m >= 2 else -1

        for i in range(1, m):
            prev_day = days[i-1]
            curr_day = days[i]
            delta_day = curr_day - prev_day
            prev_h = notes[-1][1]
            
            if generate_invalid and (i-1) == conflict_pos:
                possible_high = prev_h + delta_day + 1
                possible_low = prev_h - (delta_day + 1)
                if possible_low >= 0 and random.choice([True, False]):
                    curr_h = possible_low
                else:
                    curr_h = possible_high
                notes.append((curr_day, curr_h))
            else:
                min_h = max(prev_h - delta_day, 0)
                max_h = prev_h + delta_day
                curr_h = random.randint(min_h, max_h)
                notes.append((curr_day, curr_h))
        
        case = {
            'n': n,
            'm': m,
            'notes': notes,
        }
        case['correct_answer'] = self.calculate_answer(case)
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        notes = question_case['notes']
        prompt = f"""你是一位徒步旅行者，正在查阅旅行日记中的记录。你的旅行持续了{n}天，但只有{m}天的记录保留下来。每个记录包含当天数和当天的海拔高度。你需要根据这些记录推断出旅行过程中可能出现的最大海拔高度，或者判断这些记录是否自相矛盾。

旅行路线的高度变化规则是：相邻两天的海拔高度变化最多为1米。也就是说，如果某天的高度是h，那么第二天的高度只能是h-1、h或h+1（当然不能为负数，但允许任何非负整数）。

日记中的记录如下：

第1行包含两个整数n和m：{n} {m}
"""
        for d, h in notes:
            prompt += f"{d} {h}\n"
        prompt += """
请仔细分析可能的情况，并按照以下要求给出答案：

- 如果存在符合条件的高度序列，输出一个整数，表示可能的最大海拔峰值。
- 如果记录自相矛盾，输出大写的IMPOSSIBLE。
- 将你的最终答案放在[answer]标签内，例如：[answer]2[/answer] 或 [answer]IMPOSSIBLE[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def calculate_answer(self, case):
        n = case['n']
        m = case['m']
        notes = case['notes']
        if m == 0:
            return 'IMPOSSIBLE'

        arr = [(d-1, h) for d, h in notes]
        flag = True
        ans = 0

        ans = max(arr[0][1] + arr[0][0], arr[-1][1] + (n - arr[-1][0] - 1))

        for i in range(m-1):
            delta_d = arr[i+1][0] - arr[i][0]
            delta_h = abs(arr[i][1] - arr[i+1][1])
            if delta_h > delta_d:
                flag = False
                break  # Early termination on conflict
            a = -arr[i][0] + arr[i][1]
            b = arr[i+1][0] + arr[i+1][1]
            current_max = (a + b) // 2
            ans = max(ans, current_max)

        return ans if flag else 'IMPOSSIBLE'
