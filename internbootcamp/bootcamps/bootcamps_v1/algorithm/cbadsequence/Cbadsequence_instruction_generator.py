import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CbadsequenceInstructionGenerator(BaseInstructionGenerator):
    """Cbadsequence Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cbadsequence指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场类，设置默认参数
        """
        self.params = {
            'n': 100  # 默认生成的括号序列长度为100
        }
        self.params.update(params)
        # 确保n为偶数
        self.params['n'] = self.params['n'] if self.params['n'] % 2 == 0 else self.params['n'] - 1
    
    def case_generator(self):
        """
        生成一个括号序列的问题实例，确保可以通过移动最多一个括号使其正确
        """
        n = self.params['n']
        k = n // 2
        
        # 确保生成的括号数量是平衡的
        while True:
            s = []
            open_count = 0
            close_count = 0
            # 生成一个随机的括号序列
            for _ in range(n):
                if random.random() < 0.5:
                    s.append('(')
                    open_count += 1
                else:
                    s.append(')')
                    close_count += 1
            # 确保括号数量平衡
            if open_count == close_count:
                break
        
        s = ''.join(s)
        
        return {
            "n": n,
            "s": s
        }
    
    @staticmethod
    def prompt_func(question_case):
        """
        将问题实例转换为文本形式的问题描述
        """
        n = question_case['n']
        s = question_case['s']
        prompt = f"括号序列长度为{n}，序列为：{s}\n\nPetya可以移动最多一个括号，使得序列变成正确的括号序列吗？\n\n正确的括号序列的定义是：\n1. 空序列；\n2. 形如(t)，其中t是正确的序列；\n3. 形如t1t2，其中t1和t2都是正确的序列。\n\n你的任务是判断是否可以通过移动最多一个括号使得序列正确。如果是，输出'Yes'，否则输出'No'。请将答案放在[answer]标签中。例如：\n[answer]Yes[/answer] 或者 [answer]No[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

