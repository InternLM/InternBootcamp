import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import permutations




class KorlogiccanonicalpropositionsInstructionGenerator(BaseInstructionGenerator):
    """Korlogiccanonicalpropositions Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Korlogiccanonicalpropositions指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.variable_pool = params.get('variable_pool', [
            "operate legally for reasonable profits",
            "price fraud occurs",
            "abuse of vulnerable groups",
            "reasonable sports collisions", 
            "disruptive behavior in cultural venues",
            "tobacco use in public areas",
            "contract fulfillment",
            "citizens' rights protection",
            "youth development support",
            "national property protection",
            "noise in quiet zones",
            "remarriage rights"
        ])
        self.formula_pool = params.get('formula_pool', [
            (2, "‽p←→¬§p", "Prohibition-Permission Negation"),
            (3, "§p←→¬‽p", "Permission-Prohibition Duality"),
            (5, "¶p→¬‽p", "Obligation-Prohibition Exclusion"),
            (7, "¬§p→§¬p", "Permission Negation Implication"),
            (9, "¶p→§p", "Obligation-Permission Entailment"),
            (10, "‽p→§¬p", "Prohibition-Permission Consequence")
        ])
        self.relation_definitions = {
            '*': "Cannot be true/false together",
            'x': "Cannot both be true",
            '@': "Cannot both be false",
            '%': "No mutual exclusion"
        }
    
    def case_generator(self):
        case_type = random.choices(
            population=['relationship', 'symbolization', 'formula'],
            weights=[0.4, 0.3, 0.3],
            k=1
        )[0]
        
        if case_type == 'relationship':
            return self._gen_relationship_case()
        elif case_type == 'symbolization':
            return self._gen_symbolization_case()
        else:
            return self._gen_formula_case()
    
    @staticmethod
    def prompt_func(case):
        if case["type"] == "relationship":
            prompt = [
                "Analyze the normative relationships between these statement pairs:",
                "\n".join([f"Pair {i+1}:\n   a. {pair[0]}\n   b. {pair[1]}" 
                          for i, pair in enumerate(case["pairs"])]),
                "\nRelationship Types:",
                *[f"{opt}: {case['relation_definitions'][opt[2:]]}" 
                  for opt in case["options"]],
                "Answer format: [[SELECTION;SELECTION]] (e.g. [[A;C]])"
            ]
            return "\n".join(prompt)
        
        elif case["type"] == "symbolization":
            return (
                f"Symbolize the following regulation:\n{case['sentence']}\n\n"
                f"Variable definitions:\n" + 
                '\n'.join(f"{k}) {v}" for k,v in case["mapping"].items()) + 
                "\n\nUse modalities: ¶ (must), § (may), ‽ (prohibited)\n" 
                "Format answer: [[EXPRESSION]] (e.g. [[§p ∧ ‽q]])"
            )
        
        else:  # formula case
            return (
                f"{case['question']}\n\nOptions:\n" +
                '\n'.join(f"{k}) {v}" for k,v in case["options"].items()) +
                "\n\nAnswer with [[FORMULA_NUMBER]] (e.g. [[7]])"
            ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _gen_relationship_case(self):
        case = {
            "type": "relationship",
            "pairs": [],
            "options": ["A.*", "B.x", "C.@", "D.%"],
            "key": [],
            "relation_definitions": self.relation_definitions.copy()  # 修复1：添加定义信息
        }

        for _ in range(2):
            rel_type, symbol_pair = self._random_relation_pair()
            context = random.choice(self.variable_pool)

            statements = [
                self._symbol_to_natural(symbol_pair[0], context),
                self._symbol_to_natural(symbol_pair[1], context)
            ]

            case["pairs"].append(statements)
            case["key"].append(rel_type)

        return case

    def _gen_symbolization_case(self):
        variables = random.sample(self.variable_pool, 2)
        structure = random.choice([
            ("permitted", "prohibited"),
            ("mandatory", "prohibited"),
            ("prohibited", "permitted not"),
            ("mandatory", "permitted not")  # 修复3：新增结构类型
        ])

        return {
            "type": "symbolization",
            "sentence": f"{variables[0]} is {structure[0]}, but {variables[1]} is {structure[1]}.",
            "mapping": {chr(97+i): var for i, var in enumerate(variables)},
            "solution": self._structure_to_symbols(structure)
        }

    def _gen_formula_case(self):
        formula = random.choice(self.formula_pool)
        context_var = random.choice(self.variable_pool)

        premise = self._apply_formula_context(formula[1].split('←→')[0], context_var)
        options = self._generate_formula_options(formula, context_var)

        return {
            "type": "formula",
            "question": f"Which formula corresponds to: {premise}?",
            "options": options,
            "correct": formula[0]
        }

    @staticmethod
    def _random_relation_pair():
        relations = {
            '*': [('¶p', '§¬p'), ('‽p', '§p')],
            'x': [('¶p', '‽p')],
            '@': [('§p', '§¬p')],
            '%': [('¶p', '§p'), ('‽p', '§¬p')]
        }
        rel_type = random.choice(list(relations.keys()))
        return rel_type, random.choice(relations[rel_type])

    def _symbol_to_natural(self, symbol, context):
        modality_map = {
            '¶': ['must', 'is obligatory for'],
            '§': ['may', 'is permitted for'],
            '‽': ['must not', 'is prohibited for']
        }

        operator, proposition = symbol[0], symbol[1:]
        negation = "not " if '¬' in proposition else ""
        clean_prop = proposition.replace('¬', '')

        modality = random.choice(modality_map[operator])
        return f"{modality} {negation}{context}"

    def _structure_to_symbols(self, structure):
        conversion = {
            ('permitted', 'prohibited'): ('§p', '‽q'),
            ('mandatory', 'prohibited'): ('¶p', '‽q'),
            ('prohibited', 'permitted not'): ('‽p', '§¬q'),
            ('mandatory', 'permitted not'): ('¶p', '§¬q')  # 修复3：新增转换规则
        }
        return ' ∧ '.join(conversion[structure])

    def _apply_formula_context(self, formula_part, context):
        replacements = {
            'p': context,
            '§': 'permitted',
            '¶': 'mandatory',
            '‽': 'prohibited'
        }
        for k, v in replacements.items():
            formula_part = formula_part.replace(k, v)
        return formula_part.capitalize()

    def _generate_formula_options(self, formula, context):
        options = {chr(65): f"Formula {formula[0]}: {formula[2]}"}

        # 生成干扰项（排除正确公式）
        distractors = [f for f in self.formula_pool if f[0] != formula[0]]
        random.shuffle(distractors)

        for i in range(1, 4):
            if i-1 < len(distractors):
                options[chr(65+i)] = f"Formula {distractors[i-1][0]}: {distractors[i-1][2]}"
            else:  # 如果公式池不够，补充通用干扰项
                options[chr(65+i)] = f"Formula {random.randint(1,12)}: Generic Principle"

        return options

    @staticmethod
    def _rel_type_to_option(rel_type):
        return {'*':'A', 'x':'B', '@':'C', '%':'D'}[rel_type]
