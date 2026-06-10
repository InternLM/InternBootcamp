import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class CremoveadjacentInstructionGenerator(BaseInstructionGenerator):
    """Cremoveadjacent Bootcamp指令生成器"""
    
    def __init__(self, min_length=1, max_length=100):
        """
        初始化Cremoveadjacent指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        """生成包含随机小写字母字符串的案例，覆盖全长度范围"""
        n = random.randint(self.min_length, self.max_length)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        return {'s': s}
    
    @staticmethod
    def prompt_func(question_case):
        """生成包含明确格式要求的完整问题描述"""
        s = question_case['s']
        n = len(s)
        return f"""Given a string s of length {n}: {s}
Find the maximum number of removable characters according to the rules:
1. Remove a character if adjacent to its previous Latin letter
2. Choose optimal removal sequence

Put your final answer within [answer][/answer] tags like [answer]4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_removals(s):
        """精确实现题目要求的贪心算法"""
        ans = 0
        while True:
            update_flag = False
            # 从z到a依次处理每个字符
            for char_code in range(122, 96, -1):
                current_char = chr(char_code)
                if current_char == 'a':
                    continue  # a不可删除

                prev_char = chr(char_code-1)
                while True:
                    new_s = []
                    removed = 0
                    for i in range(len(s)):
                        if s[i] == current_char:
                            left_ok = (i > 0 and s[i-1] == prev_char)
                            right_ok = (i < len(s)-1 and s[i+1] == prev_char)
                            if left_ok or right_ok:
                                ans += 1
                                removed += 1
                            else:
                                new_s.append(s[i])
                        else:
                            new_s.append(s[i])

                    if removed > 0:
                        s = ''.join(new_s)
                        update_flag = True
                    else:
                        break
            if not update_flag:
                break
        return ans
