import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from functools import reduce
from collections import defaultdict




class ByaroslavandtwostringsInstructionGenerator(BaseInstructionGenerator):
    """Byaroslavandtwostrings Bootcamp指令生成器"""
    
    def __init__(self, n=None, min_n=1, max_n=5, p_question=0.3):
        """
        初始化Byaroslavandtwostrings指令生成器
        
        Args:
            n: 参数描述
            min_n: 参数描述
            max_n: 参数描述
            p_question: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n  # Fixed length mode
        self.min_n = min(n, min_n) if n else min_n  # 确保范围有效性
        self.max_n = max(n, max_n) if n else max_n
        self.p_question = min(max(p_question, 0.0), 1.0)  # 概率范围约束
    
    def case_generator(self):
        n = self.n if self.n is not None else random.randint(self.min_n, self.max_n)
        return {
            'n': n,
            's': self._generate_template(n),
            't': self._generate_template(n)
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""给定两个长度为{question_case['n']}的字符串模板：
模板1：{question_case['s']}
模板2：{question_case['t']}

计算所有问号替换为数字的方案中，使得这两个字符串满足以下条件的方案数（模1e9+7）：
- 存在至少一个位置i使得模板1的第i位数字 > 模板2的第i位数字
- 同时存在至少一个位置j使得模板1的第j位数字 < 模板2的第j位数字

答案请置于[answer]标签内，示例：[answer]123456789[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_template(self, n):
        return ''.join(
            '?' if random.random() < self.p_question else str(random.randint(0, 9)) 
            for _ in range(n)
        )
