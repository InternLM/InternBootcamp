import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_case(words):
    count = [0] * 4  # 00, 01, 10, 11
    swap = [[] for _ in range(4)]
    items = set(words)
    
    for i, s in enumerate(words):
        a = s[0]
        b = s[-1]
        pos = int(a) * 2 + int(b)
        count[pos] += 1
        reversed_s = s[::-1]
        if reversed_s not in items:
            swap[pos].append(i + 1)  # Using 1-based index
    
    if count[1] > count[2]:
        count[1], count[2] = count[2], count[1]
        swap[1], swap[2] = swap[2], swap[1]
    
    if count[1] + count[2] == 0:
        if count[0] > 0 and count[3] > 0:
            return (-1, None)
        else:
            return (0, [])
    else:
        diff = 0
        original_count_01 = count[1]
        original_count_10 = count[2]
        while count[2] - count[1] > 1:
            diff += 1
            count[2] -= 1
            count[1] += 1
        i = 1 if len(swap[1]) > len(swap[2]) else 2
        if len(swap[i]) >= diff:
            indexes = swap[i][:diff]
            return (diff, indexes)
        else:
            return (-1, None)


class DletsplaythewordsInstructionGenerator(BaseInstructionGenerator):
    """Dletsplaythewords Bootcamp指令生成器"""
    
    def __init__(self, min_words=1, max_words=5, min_length=1, max_length=5, **kwargs):
        """
        初始化Dletsplaythewords指令生成器
        
        Args:
            min_words: 参数描述
            max_words: 参数描述
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_words = min_words
        self.max_words = max_words
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        n = random.randint(self.min_words, self.max_words)
        existing = set()
        words = []
        for _ in range(n):
            while True:
                length = random.randint(self.min_length, self.max_length)
                word = ''.join(random.choice('01') for _ in range(length))
                if word not in existing:
                    break
            existing.add(word)
            words.append(word)
        correct_k, correct_indexes = solve_case(words)
        return {
            'n': n,
            'words': words,
            'correct_k': correct_k,
            'correct_indexes': correct_indexes if correct_k != -1 else None
        }
    
    @staticmethod
    def prompt_func(question_case):
        words = question_case['words']
        n = question_case['n']
        example_input = f"{n}\n" + '\n'.join(words)
        prompt = f"""Polycarp has a set of {n} distinct binary words. Your task is to reverse the minimal number of words so that all words remain unique and can be arranged in a sequence where each subsequent word starts with the last character of the previous word.

Input:
{example_input}

Output format:
- If impossible, output -1.
- If possible, output k (the minimal number of reversals). If k > 0, the next line should list the 1-based indices of the words to reverse.

Put your final answer within [answer] and [/answer] tags. Example:

[answer]
1
3 
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

