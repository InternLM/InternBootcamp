import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CstlInstructionGenerator(BaseInstructionGenerator):
    """Cstl Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cstl指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_depth = params.get('max_depth', 3)
        self.min_n = params.get('min_n', 1)
        self.max_n = params.get('max_n', 1000)
    
    def case_generator(self):
        # 生成一个合法的类型结构
        structure = self.generate_random_structure(current_depth=1)
        s = self.structure_to_s(structure)
        correct_answer = self.structure_to_str(structure)
        n = self.count_ints(structure)
        return {
            'n': n,
            's': s,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = ' '.join(question_case['s'])
        prompt = f"Vasya需要帮助Gena添加标点符号，使得输入的类型描述合法。已知n={n}，输入的词列表为：{s}。请按照规则添加标点符号，生成正确的类型描述。规则如下：\n"
        prompt += "1. 类型可以是'int'或者'pair<type1,type2>'，其中type1和type2也是合法类型。\n"
        prompt += "2. 生成的类型必须唯一且合法，否则输出'Error occurred'。\n"
        prompt += "请将最终答案放在[answer]标签中，例如：[answer]pair<int,int>[/answer]。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_random_structure(self, current_depth=1):
        # 避免生成过深的结构
        if current_depth > self.max_depth:
            return 'int'
        # 50% 的概率生成 'int'，50% 的概率生成 'pair'
        if random.random() < 0.5:
            return 'int'
        else:
            left = self.generate_random_structure(current_depth + 1)
            right = self.generate_random_structure(current_depth + 1)
            return ('pair', left, right)

    def structure_to_s(self, structure):
        if structure == 'int':
            return ['int']
        else:
            s = ['pair']
            s += self.structure_to_s(structure[1])
            s += self.structure_to_s(structure[2])
            return s

    def structure_to_str(self, structure):
        if structure == 'int':
            return 'int'
        else:
            left = self.structure_to_str(structure[1])
            right = self.structure_to_str(structure[2])
            return f'pair<{left},{right}>'

    def count_ints(self, structure):
        if structure == 'int':
            return 1
        else:
            return self.count_ints(structure[1]) + self.count_ints(structure[2])
