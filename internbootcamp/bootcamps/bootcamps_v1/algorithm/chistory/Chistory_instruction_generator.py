import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ChistoryInstructionGenerator(BaseInstructionGenerator):
    """Chistory Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Chistory指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = n
    
    def case_generator(self):
        events = []
        a_start = 1
        b_start = a_start + 2 * (self.n - 1) + 1
        
        for i in range(self.n):
            a = a_start + i
            b = b_start - i
            events.append([a, b])
        
        random.shuffle(events)
        
        return {
            'n': self.n,
            'events': events
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        events = question_case['events']
        input_lines = [f"{a} {b}" for a, b in events]
        input_str = f"{n}\n" + "\n".join(input_lines)
        prompt = f"""Polycarpus正在学习历史，需要帮助解决一个事件包含的问题。事件的规则如下：

- 世界历史包含n个事件，每个事件i从年份a_i开始，到年份b_i结束（a_i < b_i）。
- 任何两个事件的起始年和结束年互不相同。即，所有a_i和b_i都是唯一的。
- 我们称事件j包含事件i，当且仅当a_j < a_i且b_i < b_j。
- 你的任务是找出有多少个事件被其他事件包含。

输入格式：
第一行是一个整数n，表示事件的数量。
接下来n行每行包含两个整数a_i和b_i，表示每个事件的起始和结束年份。

输出格式：
输出一个整数，表示被其他事件包含的事件数量。

现在，你需要解决以下具体案例：

输入：
{input_str}

请仔细思考，按照正确的格式输出答案，并将最终答案放在[answer]标签内，例如：[answer]42[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

