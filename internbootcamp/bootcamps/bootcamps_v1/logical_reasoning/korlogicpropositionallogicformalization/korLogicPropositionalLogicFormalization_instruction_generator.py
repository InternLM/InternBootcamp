import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class KorlogicpropositionallogicformalizationInstructionGenerator(BaseInstructionGenerator):
    """Korlogicpropositionallogicformalization Bootcamp指令生成器"""
    
    def __init__(self, problem_type='symbolize', num_propositions=3, max_questions=3, allowed_connectives=None):
        """
        初始化Korlogicpropositionallogicformalization指令生成器
        
        Args:
            problem_type: 参数描述
            num_propositions: 参数描述
            max_questions: 参数描述
            allowed_connectives: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.problem_type = problem_type
        self.num_propositions = num_propositions
        self.max_questions = max_questions
        self.allowed_connectives = allowed_connectives if allowed_connectives is not None else ['&', '||', '~']
        self.proposition_templates = [
            "is even", "is odd", "is a prime number", "is a common color",
            "is divisible by 3", "is a fruit", "is considered lucky"
        ]
        self.subjects = ["2", "4", "5", "7", "Blue", "Red", "Square root of 3", "Pi"]
    
    def case_generator(self):
        if self.problem_type == 'symbolize':
            propositions = self._generate_propositions()
            questions, answers = self._generate_symbolize_questions(propositions)
            return {
                'type': 'symbolize',
                'propositions': propositions,
                'questions': questions,
                'answers': answers
            }
        else:
            raise NotImplementedError("Other problem types are not implemented yet.")
    
    @staticmethod
    def prompt_func(question_case):
        prop_text = "Given:\n" + "\n".join(
            [f"{var}: {desc}" for var, desc in question_case['propositions'].items()]
        )
        questions_text = "Symbolize the following propositions using &, ||, ~:\n" + "\n".join(
            [f"({i+1}) {q}" for i, q in enumerate(question_case['questions'])]
        )
        return f"{prop_text}\n\n{questions_text}\n\nFormat your answers as [[...];[...];...]" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_propositions(self):
        propositions = {}
        used_subjects = set()
        for i in range(self.num_propositions):
            while True:
                subject = random.choice(self.subjects)
                if subject not in used_subjects:
                    used_subjects.add(subject)
                    prop = random.choice(self.proposition_templates)
                    propositions[f'p{i+1}'] = f"{subject} {prop}."
                    break
        return propositions

    def _generate_symbolize_questions(self, propositions):
        questions = []
        answers = []
        variables = list(propositions.keys())
        for _ in range(self.max_questions):
            formula = self._generate_formula(variables)
            question_text = self._formula_to_natural_language(formula, propositions)
            questions.append(question_text)
            answers.append(formula)
        return questions, answers

    def _generate_formula(self, variables, depth=0):
        if depth >= 2 or len(variables) < 2:
            return random.choice(variables)

        connective = random.choice(self.allowed_connectives)
        if connective == '~':
            sub = self._generate_formula(variables, depth+1)
            return f'~{sub}'
        else:
            left = self._generate_formula(variables, depth+1)
            right = self._generate_formula(variables, depth+1)
            return f'({left}{connective}{right})'

    def _formula_to_natural_language(self, formula, propositions):
        formula = formula.replace('(', '').replace(')', '')
        parts = re.split(r'(&|\|\||~)', formula)
        parts = [p for p in parts if p]

        stack = []
        for part in parts:
            if part in ['&', '||', '~']:
                stack.append(part)
            else:
                stack.append(propositions.get(part, part))

        natural = []
        prev_op = None
        for item in stack:
            if item == '&':
                natural.append("and")
            elif item == '||':
                natural.append("or")
            elif item == '~':
                natural.append("It is not the case that")
            else:
                if prev_op == '~':
                    natural[-1] += f" {item}"
                else:
                    natural.append(item)
            prev_op = item if item in ['&', '||', '~'] else None

        return ' '.join(natural).replace(' .', '.')

    @staticmethod
    def normalize(formula):
        return formula.replace(' ', '').replace('(', '').replace(')', '')
