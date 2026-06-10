import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DmahmoudandehabandthebinarystringInstructionGenerator(BaseInstructionGenerator):
    """Dmahmoudandehabandthebinarystring Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=1000):
        """
        初始化Dmahmoudandehabandthebinarystring指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': min_n,
            'max_n': max_n
        }
    
    def case_generator(self):
        n = random.randint(self.params['min_n'], self.params['max_n'])
        # 保证至少各有一个0和1的生成方式
        hidden = ['0'] * n
        ones_pos = random.sample(range(n), k=random.randint(1, n-1))
        for pos in ones_pos:
            hidden[pos] = '1'
        # 确保至少一个0（当全1时替换最后一个）
        if len(ones_pos) == n:
            hidden[-1] = '0'
        # 确保至少一个1（当全0时随机替换）
        if not any(c == '1' for c in hidden):
            hidden[random.randint(0, n-1)] = '1'
        return {'n': n, 'hidden_str': ''.join(hidden)}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""根据以下交互规则找到二进制字符串中的0和1位置：
1. 初始字符串长度：{n}
2. 每次询问格式：? [binary_string]
3. 最终答案格式：! [pos0] [pos1]（1-based索引）
请将最终答案用[answer]标签包裹，示例：[answer]! 2 5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

