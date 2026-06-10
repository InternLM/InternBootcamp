import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import OrderedDict




class KorlogicpredicatelogicformalizationInstructionGenerator(BaseInstructionGenerator):
    """Korlogicpredicatelogicformalization Bootcamp指令生成器"""
    
    def __init__(self, num_problems=3, max_quantifiers=3):
        """
        初始化Korlogicpredicatelogicformalization指令生成器
        
        Args:
            num_problems: 参数描述
            max_quantifiers: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.num_problems = num_problems
        self.max_quantifiers = max_quantifiers
        self.problem_templates = [
            self._create_universal_implication,
            self._create_existential_conjunction,
            self._create_0ary_predicate,
            self._create_nested_quantifiers,
            self._create_negation_case,
            self._create_multiple_quantifiers
        ]
    
    def case_generator(self):
        problems = []
        selected_templates = random.choices(self.problem_templates, k=self.num_problems)
        
        for template in selected_templates:
            problems.append(template())
        
        return {
            "problems": problems,
            "answer_format": f"[[{';'.join(['answer']*self.num_problems)}]]"
        }
    
    @staticmethod
    def prompt_func(question_case):
        prompt = """In first-order logic, symbolize the following propositions using the given predicates.
Strictly follow these notation rules:
- Universal Quantifier: Ax (for all x)
- Existential Quantifier: Ex (there exists x)
- Logical Connectives: & (and), | (or), ⇒ (implies), ∼ (not)
- Predicate format: Use capitalized letters with variables (e.g., F(x), G(x,y))
- 0-ary predicates must use constants (e.g., F(a), G(b,c))

"""
        for idx, problem in enumerate(question_case["problems"], 1):
            prompt += f"\nProblem {idx}: {problem['description']}\n"
            prompt += "Predicates:\n"
            for pred, definition in OrderedDict(sorted(problem["predicates"].items())).items():
                prompt += f"- {pred}: {definition}\n"
        
        prompt += "\nProvide answers in [[answer1;answer2;...]] format exactly as required."
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _normalize(expr):
        return expr.replace(' ', '').upper()

    def _create_universal_implication(self):
        domain_map = {
            "humans": ["breathe", "are mortal"],
            "students": ["study hard", "attend classes"],
            "prime numbers": ["are even", "are greater than 2"],
            "birds": ["fly", "have feathers"],
        }
        subject, conditions = random.choice(list(domain_map.items()))
        condition = random.choice(conditions)

        return {
            "description": f"Using universal domain: All {subject} {condition}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(x)": f"x {condition}"
            },
            "correct_answer": "Ax(F(x)⇒G(x))"
        }

    def _create_existential_conjunction(self):
        entities = {
            "rabbits": ["run fast", "have long ears"],
            "cars": ["are red", "have turbo engines"],
            "apples": ["are sweet", "are organic"],
            "turtles": ["swim slowly", "have hard shells"],
        }
        subject, properties = random.choice(list(entities.items()))
        prop = random.choice(properties)

        return {
            "description": f"Using universal domain: Some {subject} {prop}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(x)": f"x {prop}"
            },
            "correct_answer": "Ex(F(x)&G(x))"
        }

    def _create_0ary_predicate(self):
        constants = ["a", "b", "c", "d"]
        templates = [
            ("{c} is both {p1} and {p2}", "&"),
            ("If {c1} is {p} then {c2} is {p}", "⇒"),
            ("Either {c1} is {p} or {c2} is {p}", "|"),
            ("Neither {c1} nor {c2} is {p}", "∼{0}&∼{1}")
        ]
        template, conn = random.choice(templates)

        if template.count("{c}") == 1:
            c = random.choice(constants)
            p1, p2 = random.sample(["F", "G", "H"], 2)
            return {
                "description": template.format(c=c, p1=p1, p2=p2),
                "predicates": {
                    f"{p1}({c})": f"{c} has property {p1}",
                    f"{p2}({c})": f"{c} has property {p2}"
                },
                "correct_answer": f"{p1}({c}){conn}{p2}({c})"
            }
        else:
            c1, c2 = random.sample(constants, 2)
            p = random.choice(["F", "G"])
            if "Neither" in template:
                answer = conn.format(f"{p}({c1})", f"{p}({c2})")
            else:
                answer = f"{p}({c1}){conn}{p}({c2})"
            return {
                "description": template.format(c1=c1, c2=c2, p=p),
                "predicates": {
                    f"{p}({c1})": f"{c1} has property {p}",
                    f"{p}({c2})": f"{c2} has property {p}"
                },
                "correct_answer": answer
            }

    def _create_nested_quantifiers(self):
        relations = {
            "faster than": ["rabbits", "turtles"],
            "smarter than": ["humans", "animals"],
            "older than": ["students", "teachers"],
        }
        rel_desc, (subject, obj) = random.choice(list(relations.items()))

        return {
            "description": f"Symbolize: Some {subject} are {rel_desc} all {obj}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(y)": f"y is a {obj}",
                "H(x,y)": f"x is {rel_desc} y"
            },
            "correct_answer": "Ex(F(x)&Ay(G(y)⇒H(x,y)))"
        }

    def _create_negation_case(self):
        return {
            "description": "No humans can fly. (Using universal domain)",
            "predicates": {
                "F(x)": "x is human",
                "G(x)": "x can fly"
            },
            "correct_answer": "Ax(F(x)⇒∼G(x))"
        }

    def _create_multiple_quantifiers(self):
        return {
            "description": "Every person has someone they love. (Domain: people)",
            "predicates": {
                "F(x,y)": "x loves y"
            },
            "correct_answer": "AxEyF(x,y)"
        }
