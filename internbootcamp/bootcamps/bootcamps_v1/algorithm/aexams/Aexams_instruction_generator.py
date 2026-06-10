import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class AexamsInstructionGenerator(BaseInstructionGenerator):
    """Aexams Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, max_ai=10**9):
        """
        初始化Aexams指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_ai: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_ai = max_ai
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        exams = []
        for _ in range(n):
            ai = random.randint(2, self.max_ai)
            bi = random.randint(1, ai - 1)
            exams.append((ai, bi))
        return {
            'n': n,
            'exams': exams
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        exams = question_case['exams']
        exam_lines = '\n'.join([f"{a} {b}" for a, b in exams])
        prompt = f"""Valera需要参加{n}场考试。每场考试可以选择在提前日bi或原定日ai进行考试，其中bi < ai。记录本上的日期按ai非递减排列，求最后考试的最早可能日期。

输入格式：
第一行是n，表示考试数量。
接下来n行每行两个整数ai和bi（bi < ai）。

例如输入：
3
5 2
3 1
4 2
正确输出是2，最后考试在第2天。

当前输入：
{n}
{exam_lines}

请计算答案并放在[answer]和[/answer]之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

