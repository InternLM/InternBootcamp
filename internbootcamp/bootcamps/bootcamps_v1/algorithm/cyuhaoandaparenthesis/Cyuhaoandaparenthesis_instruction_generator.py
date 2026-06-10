import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CyuhaoandaparenthesisInstructionGenerator(BaseInstructionGenerator):
    """Cyuhaoandaparenthesis Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cyuhaoandaparenthesis指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'max_opening_pairs': 3,
            'max_balanced_pairs': 2,
            'max_invalid_sequences': 2,
            'max_unmatched_sequences': 2,
        }
        self.params.update(params)
        super().__init__(**params)  # 修复：添加基类初始化
    
    def case_generator(self):
        max_op = self.params['max_opening_pairs']
        max_bal = self.params['max_balanced_pairs']
        max_inv = self.params['max_invalid_sequences']
        max_unm = self.params['max_unmatched_sequences']

        while True:
            m = random.randint(0, max_op)
            k = random.randint(0, max_bal)
            i = random.randint(0, max_inv)
            j = random.randint(0, max_unm)
            
            sequences = []
            # 生成成对的可匹配序列
            for _ in range(m):
                x = random.randint(1, 3)
                sequences.append('(' * x)
                sequences.append(')' * x)
            
            # 生成平衡序列对
            for _ in range(k):
                sequences.append(self.generate_balanced())
                sequences.append(self.generate_balanced())
            
            # 生成无效序列（同时含有开闭括号残留）
            for _ in range(i):
                sequences.append(self.generate_invalid())
            
            # 生成大长度单边序列
            for _ in range(j):
                x = random.randint(4, 5)
                sequences.append(random.choice(['(', ')']) * x)
            
            if sequences:
                break
            else:  # Fallback机制
                sequences.append(self.generate_balanced())

        random.shuffle(sequences)
        return {'n': len(sequences), 'sequences': sequences}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        sequences = "\n".join(question_case['sequences'])
        return f"""请解决括号配对问题。给定n个括号序列，找出最大可配对数量。
        
输入格式：
第一行：n
接下来n行：各括号序列

示例：
输入：
7
)())
)
((
((
(
)
输出：
2

当前输入数据：
n = {question_case['n']}
{sequences}

将答案放入[answer]标签内，如：[answer]3[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_balanced(self):
        k = random.randint(1, 3)
        if random.choice([True, False]):
            return '()' * k  # 扁平结构
        return '(' * k + ')' * k  # 嵌套结构

    def generate_invalid(self):
        # 保证处理后同时含有两种括号的无效序列
        invalid_pool = [
            ')(', 
            '())(',
            '(()))(',
            ')((()',
            ')()(',
            ')))(((', 
            ')())(('
        ]
        return random.choice(invalid_pool)
