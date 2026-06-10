import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CremovingcolumnsInstructionGenerator(BaseInstructionGenerator):
    """Cremovingcolumns Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, m_min=1, m_max=10):
        """
        初始化Cremovingcolumns指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        rows = [''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(m)) for _ in range(n)]
        correct_answer = self.compute_min_removals(n, m, rows)
        return {
            'n': n,
            'm': m,
            'rows': rows,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        rows = question_case['rows']
        input_lines = [f"{n} {m}"] + rows
        input_block = '\n'.join(input_lines)
        problem_text = f"""You are given a {n}×{m} rectangular table of lowercase English letters. Your task is to determine the minimum number of columns you need to remove so that the remaining table's rows are ordered lexicographically from top to bottom.

Lexicographical order is defined as follows: two strings are compared based on the first position where they differ. The string with the smaller character at that position is considered lexicographically smaller. If one string is a prefix of the other, the shorter string is considered smaller.

For example, after removing the second column from the table:

abcd
edfg
hijk

the resulting table is:

acd
efg
hjk

Your goal is to find the minimum number of columns that must be removed to make the table good. A table is considered good if each row is lexicographically no larger than the next row.

Input format:
- The first line contains two integers n (number of rows) and m (number of columns).
- The next n lines each contain exactly m lowercase letters representing the table.

Now, solve the following specific case:

Input:
{input_block}

Please provide your answer as a single integer enclosed within [answer] and [/answer] tags. For example, if your answer is 3, write it as [answer]3[/answer]."""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_removals(n, m, rows):
        if n <= 1:
            return 0
        deleted = set()
        fixed = [False] * (n-1)
        for col in range(m):
            delete_col = False
            for i in range(n-1):
                if fixed[i]:
                    continue
                if rows[i][col] > rows[i+1][col]:
                    delete_col = True
                    break
            if delete_col:
                deleted.add(col)
            else:
                for i in range(n-1):
                    if not fixed[i] and rows[i][col] < rows[i+1][col]:
                        fixed[i] = True
        return len(deleted)
