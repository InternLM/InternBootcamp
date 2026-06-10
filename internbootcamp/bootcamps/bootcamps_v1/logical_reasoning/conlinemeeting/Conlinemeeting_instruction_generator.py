import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def calculate_solution(n, messages):
    entered = set()
    prefix = []
    for sign, num in messages:
        if sign == '+':
            entered.add(num)
        else:
            if num not in entered:
                prefix.append(('+', num))
    prefix.reverse()
    full_messages = prefix + messages
    online = set()
    leaders = set(range(1, n+1))
    prev_sign = None
    prev_num = 0
    
    for m in full_messages:
        sign, num = m
        if prev_sign is not None and prev_sign != sign and prev_num != num:
            if num in leaders:
                leaders.remove(num)
            if prev_num in leaders:
                leaders.remove(prev_num)
        if sign == '+':
            if len(online) > 0 and num in leaders:
                leaders.remove(num)
            online.add(num)
        else:
            if num in online:
                online.remove(num)
            if len(online) > 0 and num in leaders:
                leaders.remove(num)
        prev_sign, prev_num = sign, num
    return sorted(leaders) if leaders else []


class ConlinemeetingInstructionGenerator(BaseInstructionGenerator):
    """Conlinemeeting Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=20):
        """
        初始化Conlinemeeting指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        messages = []
        online = set()
        
        for _ in range(m):
            available_ops = []
            if online:
                available_ops.append('-')
            if len(online) < n:
                available_ops.append('+')
            if not available_ops:
                break
            
            sign = random.choice(available_ops)
            if sign == '+':
                available_users = list(set(range(1, n+1)) - online)
                user_id = random.choice(available_users)
                online.add(user_id)
            else:
                user_id = random.choice(list(online))
                online.remove(user_id)
            messages.append((sign, user_id))
        
        while len(messages) < m:
            available_ops = []
            if online:
                available_ops.append('-')
            if len(online) < n:
                available_ops.append('+')
            if not available_ops:
                break
            
            sign = random.choice(available_ops)
            if sign == '+':
                available_users = list(set(range(1, n+1)) - online)
                user_id = random.choice(available_users)
                online.add(user_id)
            else:
                user_id = random.choice(list(online))
                online.remove(user_id)
            messages.append((sign, user_id))
        
        expected_leaders = calculate_solution(n, messages)
        return {
            'n': n,
            'm': len(messages),
            'messages': messages,
            'expected_leaders': expected_leaders
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        messages = question_case['messages']
        input_lines = [f"{n} {m}"] + [f"{sign} {user_id}" for sign, user_id in messages]
        input_str = '\n'.join(input_lines)
        prompt = f"""You are the assistant director of company F. Given the login/logout records of an online meeting, determine all possible team leaders. The leader must be present whenever at least one person is online during the recorded period.

Input format:
- First line: two integers n (number of team members) and m (number of messages)
- Following m lines: Each line is '+ id' (login) or '- id' (logout)

Output requirements:
- If there are possible leaders: 
  First line: k (number of leaders)
  Second line: k IDs in increasing order
- If no possible leaders: 
  Single line: 0

Put your final answer within [answer] and [/answer]. For example:
[answer]
3
2 4 5
[/answer]

Input data:
{input_str}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

