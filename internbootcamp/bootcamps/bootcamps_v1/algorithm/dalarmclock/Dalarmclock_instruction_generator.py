import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from bisect import bisect_left
from bisect import bisect_right




class DalarmclockInstructionGenerator(BaseInstructionGenerator):
    """Dalarmclock Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=100, max_time=1000):
        """
        初始化Dalarmclock指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_time: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)
        self.max_m = max(max_m, 1)
        self.max_time = max(max_time, self.max_n + 2)  # 保证足够的时间点生成
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(1, n)
        m = random.randint(1, self.max_m)
        
        # 生成n个唯一且可能的时间点（确保足够的时间空间）
        possible_times = list(range(1, self.max_time + 1))
        ai = random.sample(possible_times, n)
        
        # 计算正确答案
        ai_sorted = sorted(ai)
        ans = self.calculate_min_turn_off(n, m, k, ai_sorted)
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'alarms': ai,  # 保持原始输入顺序
            'ans': ans
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        alarm_list = ' '.join(map(str, question_case['alarms']))
        return f"""根据以下条件计算需要关闭的最小闹钟数：
- 总闹钟数：{question_case['n']}
- 危险窗口时长：{question_case['m']}分钟
- 唤醒阈值：{question_case['k']}个闹钟
- 闹钟时间（原始无序输入）：{alarm_list}

请将最终答案放在[answer]和[/answer]标记之间，例如：[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_turn_off(n, m, k, a_sorted):
        s = []
        ans = 0
        for x in a_sorted:
            # 维护滑动窗口
            while s and x - s[0] >= m:
                del s[0]
            if len(s) + 1 < k:
                s.append(x)
            else:
                ans += 1
        return ans
