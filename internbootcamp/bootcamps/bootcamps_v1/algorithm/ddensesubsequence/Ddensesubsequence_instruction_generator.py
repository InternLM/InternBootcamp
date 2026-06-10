import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve(m, s):
    n = len(s)
    if n == 0 or m == 0:
        return ""
    
    # Frequency list generation
    sorted_chars = sorted(s)
    freq = []
    current_char = sorted_chars[0]
    count = 1
    
    for c in sorted_chars[1:]:
        if c == current_char:
            count += 1
        else:
            freq.append((current_char, count))
            current_char = c
            count = 1
    freq.append((current_char, count))
    
    # Find minimal solution
    for idx, (char, total) in enumerate(freq):
        required = 0
        last_covered = -1
        last_candidate = -1
        valid = True
        
        for i in range(n):
            if s[i] < char:
                last_covered = i
                last_candidate = i
            elif s[i] == char:
                last_candidate = i
            
            # Check window violation
            if i - last_covered >= m:
                if last_candidate > last_covered:
                    required += 1
                    last_covered = last_candidate
                else:
                    valid = False
                    break
        
        # Final check for the last window
        if valid and (n - last_covered) > m:
            valid = False
        
        if valid:
            # Calculate required count
            min_chars = []
            for c, _ in freq[:idx+1]:
                if c < char:
                    min_chars.append(c)
            return char * required + ''.join(sorted(min_chars))
        else:
            continue
    
    # Fallback to all smallest characters
    return ''.join(sorted(s))


class DdensesubsequenceInstructionGenerator(BaseInstructionGenerator):
    """Ddensesubsequence Bootcamp指令生成器"""
    
    def __init__(self, max_s_length=20, test_edge_cases=True):
        """
        初始化Ddensesubsequence指令生成器
        
        Args:
            max_s_length: 参数描述
            test_edge_cases: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_s_length = max_s_length
        self.test_edge_cases = test_edge_cases
        self.edge_cases = [
            {'m': 1, 's': 'abcde'},        # m=1必须全选
            {'m': 5, 's': 'aaaaa'},        # 全相同字符
            {'m': 3, 's': 'abababa'},      # 交错模式
            {'m': 4, 's': 'aabbaacc'},     # 重复模式
            {'m': 2, 's': 'zxyx'},         # 包含局部最小值
            {'m': 5, 's': 'edcba'},        # 递减序列
            {'m': 3, 's': 'abb'}
        ]
    
    def case_generator(self):
        if self.test_edge_cases and random.random() < 0.7:
            case = random.choice(self.edge_cases)
            m = case['m']
            s = case['s']
        else:
            len_s = random.randint(m_min := 1, self.max_s_length)
            m = random.randint(1, len_s)
            s = ''.join(random.choices(string.ascii_lowercase, k=len_s))
        
        # 确保m不超过s长度
        m = min(m, len(s))
        return {
            'm': m,
            's': s,
            'expected': solve(m, s)
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""Given string s = "{question_case['s']}" and m = {question_case['m']}, find the lex smallest string by selecting positions that cover all m-length windows. Put your final answer between [answer] and [/answer]. Example: [answer]abc[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

