import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Koroperationunicode25ceInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25ce Bootcamp指令生成器"""
    
    def __init__(self, min_val=-10, max_val=10, equation_prob=0.4):
        """
        初始化Koroperationunicode25ce指令生成器
        
        Args:
            min_val: 参数描述
            max_val: 参数描述
            equation_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_val = min_val
        self.max_val = max_val
        self.equation_prob = equation_prob
        self.operators = ['+', '-', '*']
    
    def case_generator(self):
        if random.random() < self.equation_prob:
            return self._generate_equation_case()
        else:
            op = random.choice(self.operators)
            terms = [
                (random.randint(self.min_val, self.max_val), 
                 random.randint(self.min_val, self.max_val))
                for _ in range(2)
            ]
            res1 = self.compute_operator(*terms[0])
            res2 = self.compute_operator(*terms[1])
            
            if op == '+':
                real = res1[0] + res2[0]
                imag = res1[1] + res2[1]
            elif op == '-':
                real = res1[0] - res2[0]
                imag = res1[1] - res2[1]
            else:
                real = res1[0]*res2[0] - res1[1]*res2[1]
                imag = res1[0]*res2[1] + res1[1]*res2[0]
            
            return {
                'type': 'calculation',
                'terms': terms,
                'operator': op,
                'correct': (real, imag)
            }
    
    @staticmethod
    def prompt_func(question_case):
        if question_case['type'] == 'calculation':
            (a1, b1), (a2, b2) = question_case['terms']
            op_map = {'+': '+', '-': '-', '*': '×'}
            return (
                "Define: a◎b=(a + bi)^2"
                f"Compute ({a1}◎{b1}) {op_map[question_case['operator']]} ({a2}◎{b2}).\n"
                "Format: x + yi (e.g. '3-4i', '-5')\n"
                "Put your answer within [[ ]]"
            )
        else:
            return (
                "Define: a◎b=(a + bi)^2"
                f"If {question_case['form']} = {question_case['target'][0]} + {question_case['target'][1]}i\n"
                "Find X (integer only). Wrap answer in [[ ]]"
            ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_operator(a, b):
        """计算a◎b对应的复数平方"""
        return (a**2 - b**2, 2*a*b)

    def _generate_equation_case(self):
        """生成包含多种形式的方程"""
        equation_type = random.choice([
            'basic_left', 
            'basic_right',
            'scalar_left',
            'scalar_right'
        ])

        X = random.randint(self.min_val, self.max_val)
        a = random.randint(1, 5)  # 避免a为0导致多解
        b = random.randint(self.min_val, self.max_val)
        c = random.randint(self.min_val, self.max_val)
        k = random.randint(2, 5)

        if equation_type.startswith('basic'):
            term1_real, term1_imag = self.compute_operator(X, a)
            term2_real, term2_imag = self.compute_operator(b, c)
            op = '+' if random.random() < 0.5 else '-'

            if equation_type == 'basic_left':
                # (X◎a) ± (b◎c) = target
                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'left',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }
            else:  # basic_right
                # (b◎c) ± (X◎a) = target
                target_real = term2_real + term1_real if op == '+' else term2_real - term1_real
                target_imag = term2_imag + term1_imag if op == '+' else term2_imag - term1_imag
                return {
                    'type': 'equation',
                    'form': f'({b}◎{c}) {op} (X◎{a})',
                    'x_pos': 'right',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }

        else:  # scalar类型
            scalar = k
            if equation_type == 'scalar_left':
                # (X◎a) ± k×(b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term2_real, term2_imag = self.compute_operator(b, c)
                term2_real *= scalar
                term2_imag *= scalar
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} {scalar}×({b}◎{c})',
                    'x_pos': 'left_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }
            else:  # scalar_right
                # k×(X◎a) ± (b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term1_real *= scalar
                term1_imag *= scalar
                term2_real, term2_imag = self.compute_operator(b, c)
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'{scalar}×(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'right_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }

    @staticmethod
    def parse_complex(s):
        s = s.replace(' ', '').lower().replace('i', 'j').rstrip('j')
        try:
            c = complex(s)
            return (int(c.real), int(c.imag))
        except:
            if s:
                return (int(s), 0)
            return (0, 0)
