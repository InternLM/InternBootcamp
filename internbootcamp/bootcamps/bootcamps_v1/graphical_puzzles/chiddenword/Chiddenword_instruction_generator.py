import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import string
import random




class ChiddenwordInstructionGenerator(BaseInstructionGenerator):
    """Chiddenword Bootcamp指令生成器"""
    
    def __init__(self, force_possible=None, **params):
        """
        初始化Chiddenword指令生成器
        
        Args:
            force_possible: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.force_possible = force_possible
    
    def case_generator(self):
        while True:
            letters = list(string.ascii_uppercase)
            duplicate_char = random.choice(letters)
            s_list = letters.copy()
            s_list.append(duplicate_char)
            random.shuffle(s_list)
            s = ''.join(s_list)
            
            st = s.find(duplicate_char)
            en = s.find(duplicate_char, st + 1)
            if en == -1:
                continue
            
            if self.force_possible is None:
                break
            elif self.force_possible:
                if en - st > 1:
                    break
            else:
                if en - st == 1:
                    break
        
        solution = self.generate_solution(s)
        expected_output = solution if solution != "Impossible" else solution
        return {
            's': s,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        prompt = f"""You are given a string s of 27 uppercase English letters, where each letter appears at least once. Your task is to construct a 2-row by 13-column grid where each tile contains a letter. The grid must contain a path that spells the string s when traversed consecutively. Adjacent tiles are those sharing a side or a corner. The path must visit adjacent tiles (including diagonally adjacent) in sequence. If no such grid exists, output 'Impossible'. Otherwise, output the two rows of the grid. Ensure your answer is formatted with the two rows enclosed within [answer] tags. 

Input string s: {s}

Put your answer within [answer] and [/answer] tags. For example, if the solution is:
YXWVUTGHIJKLM
ZABCDEFSRQPON
Your answer should be formatted as:
[answer]YXWVUTGHIJKLM[/answer]
[answer]ZABCDEFSRQPON[/answer]

If impossible, write:
[answer]Impossible[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_solution(s_input):
        s = s_input
        st = 0
        en = 0
        ans = [['.' for _ in range(13)] for _ in range(2)]
        found = False
        for i in range(ord('A'), ord('Z') + 1):
            c = chr(i)
            st = s.find(c)
            if st == -1:
                continue
            en = s.find(c, st + 1)
            if en != -1:
                found = True
                break
        if not found:
            return "Impossible"

        if st + 1 == en:
            return "Impossible"
        else:
            l = (en - st)
            l += l % 2
            ss = 13 - (l // 2)
            p = [ss, 0]
            dr = 1
            for i in range(st, en):
                ans[p[1]][p[0]] = s[i]
                if p[0] + dr == 13:
                    p[1] += 1
                    dr *= -1
                else:
                    p[0] += dr
            p = [ss - 1, 0]
            dr = -1
            a = s[:st]
            b = s[en + 1:]
            bf = a[::-1] + b[::-1]
            for i in range(len(bf)):
                if p[0] < 0:
                    p[0] = 0
                    p[1] = 1
                    dr = 1
                ans[p[1]][p[0]] = bf[i]
                p[0] += dr
            row0 = ''.join(ans[0])
            row1 = ''.join(ans[1])
            return [row0, row1]
