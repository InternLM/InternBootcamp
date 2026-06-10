import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class E2twilightandancientscrollharderversionInstructionGenerator(BaseInstructionGenerator):
    """E2twilightandancientscrollharderversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_word_length=5, **params):
        """
        初始化E2twilightandancientscrollharderversion指令生成器
        
        Args:
            max_n: 参数描述
            max_word_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_n = max_n
        self.max_word_length = max_word_length
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        s_list = []
        prev = ""
        for _ in range(n):
            valid = False
            for _ in range(100):
                if not s_list:
                    # Allow empty string for first word
                    length = random.randint(0, self.max_word_length)
                    if length == 0:
                        s = ''
                    else:
                        s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
                else:
                    # Generate s >= prev
                    min_len = max(len(prev), 1)  # At least 1 character to have space for insertion
                    max_len = self.max_word_length
                    length = random.randint(min_len, max_len)
                    
                    # Construct s to be >= prev
                    prefix = list(prev)
                    if len(prev) < length:
                        prefix += ['a'] * (length - len(prev))
                    else:
                        length = len(prev)
                    
                    change_pos = random.randint(0, length-1)
                    for i in range(change_pos, length):
                        if i < len(prev):
                            min_char = prev[i]
                        else:
                            min_char = 'a'
                        new_char = random.choice([chr(c) for c in range(ord(min_char), ord('z')+1)])
                        prefix[i] = new_char
                        if i >= len(prev) or ''.join(prefix[:i+1]) > prev[:i+1]:
                            # Fill remaining with 'a'
                            for j in range(i+1, length):
                                prefix[j] = 'a'
                            break
                    s = ''.join(prefix)
                
                if s >= prev:
                    prev = s
                    valid = True
                    break
            if not valid:
                s = prev  # Fall back to previous valid string
            s_list.append(s)
        
        t_list = []
        expected = 1
        for s in s_list:
            if len(s) >= self.max_word_length:
                # Cannot add character, use fallback
                ways = 1
                if s:
                    t = s + (s[-1] if random.random() < 0.5 else 'z')
                else:
                    t = 'a'
                t_list.append(t)
                expected = expected * ways % self.MOD
                continue

            if not s:
                # Original was empty, add one character
                t = 'a'
                ways = 1
            else:
                # Decide insertion type
                if random.random() < 0.5:
                    # Insert duplicate character to create multiple solutions
                    if len(s) == 0:
                        t = 'aa'
                        ways = 2
                    else:
                        insert_pos = random.randint(0, len(s)-1)
                        duplicate_char = s[insert_pos]
                        t = s[:insert_pos] + duplicate_char + s[insert_pos:]
                        # Count possible positions that restore original
                        ways = 0
                        for i in range(len(t)):
                            if t[:i] + t[i+1:] == s:
                                ways += 1
                        if ways == 0:
                            # Fallback to simple append
                            last_char = s[-1]
                            c = chr(ord(last_char) + 1) if last_char < 'z' else 'z'
                            t = s + c
                            ways = 1
                else:
                    # Simple append with larger character
                    last_char = s[-1] if s else 'a'
                    c = chr(ord(last_char) + 1) if last_char < 'z' else 'z'
                    t = s + c
                    ways = 1
            
                # Validate t length
                if len(t) > self.max_word_length:
                    t = s + (s[-1] if s else 'a')
                    ways = 1

            t_list.append(t)
            expected = expected * ways % self.MOD

        return {
            "n": len(t_list),
            "words": t_list,
            "expected": expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        words = question_case['words']
        problem = (
            "Twilight Sparkle has received a scroll where each word had exactly one letter added. "
            "Your task is to determine how many ways you can delete one letter from each word to restore "
            "the original lexicographically non-decreasing order.\n\n"
            "**Input:**\n"
            f"{n}\n" + '\n'.join(words) + "\n\n"
            "**Output:**\n"
            "A single integer representing the number of valid ways modulo 10^9+7.\n\n"
            "Place your final answer within [answer] and [/answer] tags."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

