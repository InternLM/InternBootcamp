import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_removals(n, m, table_rows):
    sol = ['' for _ in range(n)]
    count = 0
    for col_idx in range(m):
        current_col = [row[col_idx] for row in table_rows]
        temp = [sol[i] + current_col[i] for i in range(n)]
        if temp == sorted(temp):
            sol = temp
        else:
            count += 1
    return count


class AremovingcolumnsInstructionGenerator(BaseInstructionGenerator):
    """Aremovingcolumns Bootcamp指令生成器"""
    
    def __init__(self, n_range=(1, 5), m_range=(1, 5)):
        """
        初始化Aremovingcolumns指令生成器
        
        Args:
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min, self.n_max = n_range
        self.m_min, self.m_max = m_range
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        table = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=m)) for _ in range(n)]
        correct_answer = compute_min_removals(n, m, table)
        return {
            'n': n,
            'm': m,
            'table': table,
            'correct': correct_answer  # Key必须与_verify_correction一致
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['m']}"] + question_case['table']
        
        # 修复的字符串拼接结构
        problem_description = (
            "You are given a rectangular table of lowercase English letters. Your task is to determine the "
            "minimum number of columns you need to remove so that the rows become lexicographically ordered "
            "from top to bottom.\n\n"
            
            "Lexicographical Order Rules:\n"
            "1. A string 's' is lexicographically smaller than 't' if:\n"
            "   - At the first position where they differ, 's' has a character smaller than 't'\n"
            "   - All preceding characters are identical\n"
            "   - Example: 'apple' < 'apply' (diff at 4th character)\n\n"
            
            "Special Cases:\n"
            "- An empty table (all columns removed) is considered valid\n"
            "- Single-row tables are always valid (requires 0 removals)\n\n"
            
            "Input Format:\n"
            "- Line 1: Two integers n (rows) and m (columns)\n"
            "- Next n lines: Each contains exactly m lowercase letters\n\n"
            
            "Output Format:\n"  # 修复此处换行符错误
            "- A single integer indicating the minimal number of columns to remove\n\n"
            
            "Example Input 1:\n"
            "1 10\ncodeforces\n\n"
            "Example Output 1:\n[answer]0[/answer]\n\n"
            
            "Example Input 2:\n"
            "4 4\ncase\ncare\ntest\ncode\n\n"
            "Example Output 2:\n[answer]2[/answer]\n\n"
            
            "Now solve this problem:\n"
            f"{chr(10).join(input_lines)}\n"
            "Put your final answer within [answer] and [/answer] tags."
        )
        return problem_description 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

