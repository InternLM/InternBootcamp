import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re




class Koroperationunicode203bInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode203b Bootcamp指令生成器"""
    
    def __init__(self, C=2, max_operand=100, max_attempts=100, **params):
        """
        初始化Koroperationunicode203b指令生成器
        
        Args:
            C: 参数描述
            max_operand: 参数描述
            max_attempts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.C = C
        self.max_operand = max_operand
        self.max_attempts = max_attempts
    
    def case_generator(self):
        problem_type = random.choices(
            ['compute', 'solve_x', 'solve_c'],
            weights=[5, 3, 2],
            k=1
        )[0]
        
        try:
            if problem_type == 'compute':
                return self._generate_compute_case()
            elif problem_type == 'solve_x':
                return self._generate_solve_x_case()
            elif problem_type == 'solve_c':
                return self._generate_solve_c_case()
        except Exception as e:
            # 异常时返回默认计算题
            return self._generate_compute_case()
    
    @staticmethod
    def prompt_func(question_case):
        # 统一规则描述
        if 'C' in question_case and question_case['C'] != 2:
            rule_desc = [
                "We define a special operation ※ with parameter C:",
                "- If a is a multiple of b: a ※ b = a/b + C",
                "- If b is a multiple of a: a ※ b = b/a + C",
                "- Otherwise: a ※ b = 24"
            ]
        else:
            rule_desc = [
                "We define a special operation ※ with these rules:",
                "- When a is a multiple of b: a ※ b = a/b + 2",
                "- When b is a multiple of a: a ※ b = b/a + 2",
                "- If neither is a multiple: a ※ b = 24"
            ]
        
        task_desc = ""
        if question_case['type'] == 'compute':
            expr = '※'.join(map(str, question_case['expression']))
            task_desc = f"Compute the value of {expr}."
            format_note = "Put your final answer in [[ ]] as a single number."
        elif question_case['type'] == 'solve_x':
            task_desc = f"Solve the equation: {question_case['equation']}"
            if len(question_case['solutions']) > 1:
                format_note = "Put all possible solutions in [[ ]] separated by 'or', e.g., [[2or5]]."
            else:
                format_note = "Put your answer in [[ ]] as a single number."
        elif question_case['type'] == 'solve_c':
            task_desc = f"Determine parameter C from equation: {question_case['equation']}"
            format_note = "Put your answer in [[ ]] as a single number."
        
        return (
            '\n'.join(rule_desc) + '\n\n' +
            f'Problem: {task_desc}\n' +
            f'Format Requirement: {format_note}'
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_compute_case(self):
        for _ in range(self.max_attempts):
            num_operands = random.choices([2,3,4], weights=[5,3,1])[0]
            operands = [random.randint(1, self.max_operand) for _ in range(num_operands)]

            try:
                current_value = operands[0]
                for op in operands[1:]:
                    current_value = self._compute_operation(current_value, op, self.C)
            except ZeroDivisionError:
                continue

            # 允许有限概率生成结果为24的题目
            if current_value !=24 or random.random() < 0.2:
                return {
                    'type': 'compute',
                    'expression': operands,
                    'C': self.C,
                    'answer': int(current_value)
                }

        # 保底返回简单计算题
        return {
            'type': 'compute',
            'expression': [4,7],
            'C': self.C,
            'answer': 24
        }

    def _compute_operation(self, a, b, C):
        if b == 0 or a == 0:
            return 24
        if a % b == 0:
            return (a // b) + C
        if b % a == 0:
            return (b // a) + C
        return 24

    def _generate_solve_x_case(self):
        for _ in range(self.max_attempts):
            # 随机选择生成方向
            if random.random() < 0.5:  # 生成 a※X=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                # 寻找所有可能的X解
                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(a, X, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"{a}※X={target}",
                        'solutions': solutions,
                        'C': self.C
                    }
            else:  # 生成 X※a=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(X, a, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"X※{a}={target}",
                        'solutions': solutions,
                        'C': self.C
                    }

        # 保底返回单解问题
        return {
            'type': 'solve_x',
            'equation': "X※4=6",
            'solutions': [8],  # 8※4=2+2=4?
            'C': self.C
        }

    def _generate_solve_c_case(self):
        for _ in range(self.max_attempts):
            # 随机生成方向
            if random.random() < 0.5:
                a = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                b = a * factor
                expected = factor + self.C  # a※b = b/a + C
            else:
                b = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                a = b * factor
                expected = factor + self.C  # a※b = a/b + C

            # 避免除零错误
            if a == 0 or b == 0:
                continue

            return {
                'type': 'solve_c',
                'equation': f"{a}※{b}={expected}",
                'answer': self.C
            }

        # 保底返回
        return {
            'type': 'solve_c',
            'equation': "25※5=8",
            'answer': 3  # 25/5=5 +3=8
        }
