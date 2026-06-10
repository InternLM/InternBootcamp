import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class KorlogicanalogicalreasoningInstructionGenerator(BaseInstructionGenerator):
    """Korlogicanalogicalreasoning Bootcamp指令生成器"""
    
    def __init__(self, attribute_pools=None, **params):
        """
        初始化Korlogicanalogicalreasoning指令生成器
        
        Args:
            attribute_pools: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.attribute_pools = attribute_pools or {
            'university': {
                'attributes': ['an established school', 'strong faculty', 'good academic atmosphere'],
                'derived_positive': 'reached a new level after reform',
                'derived_negative': 'cannot reach a new level after reform',
                'objects': ['University F', 'University H']
            },
            'ornithology': {
                'attributes': ['black feathers', 'large beaks', 'carnivorous diet'],
                'derived_positive': 'nocturnal activity',
                'derived_negative': 'non-nocturnal activity',
                'objects': ['crows in University A', 'a bird in University B']
            },
            'astronomy': {
                'attributes': ['an atmosphere', 'liquid water', 'moderate temperatures'],
                'derived_positive': 'natural life',
                'derived_negative': 'no natural life',
                'objects': ['Earth', 'the Moon']
            },
            'marine': {
                'attributes': ['sunlight', 'stable pressure', 'moderate temperatures'],
                'derived_positive': 'terrestrial organisms',
                'derived_negative': 'no terrestrial organisms',
                'objects': ['land', 'the deep sea']
            }
        }
        self.params = params
    
    def case_generator(self):
        # Select category and method
        category_key = random.choice(list(self.attribute_pools.keys()))
        category = self.attribute_pools[category_key]
        method = random.choice(['Ψ', '⌘'])
        question_type = random.choice(['method', 'attribute'])
        
        # Generate attributes
        common_attrs = random.sample(category['attributes'], 3)
        derived_attr = category['derived_positive'] if method == 'Ψ' else category['derived_negative']
        
        # Determine correct answer
        if question_type == 'method':
            correct_answer = 'A' if method == 'Ψ' else 'B'
        else:
            # Randomly select which attribute to question
            target_is_common = random.choice([True, False])
            if method == 'Ψ':
                correct_answer = 'A' if target_is_common else 'B'
                target_attr = common_attrs[0] if target_is_common else derived_attr
            else:
                correct_answer = 'A' if target_is_common else 'B'
                target_attr = common_attrs[0] if target_is_common else derived_attr

        return {
            'question_type': question_type,
            'method': method,
            'category': category_key,
            'common_attrs': common_attrs,
            'derived_attr': derived_attr,
            'objects': category['objects'],
            'correct_answer': correct_answer,
            'target_attr': target_attr if question_type == 'attribute' else None
        }
    
    @staticmethod
    def prompt_func(case):
        # Contextual templates
        method_descriptions = {
            'Ψ': {
                'premise': "{objA} has {attrs}. {objB} has {common_attrs}.",
                'conclusion': "Therefore, {objB} also has {derived_attr}."
            },
            '⌘': {
                'premise': "{objA} has {attrs}. {objB} does not have {common_attrs}.",
                'conclusion': "Therefore, {objB} does not have {derived_attr}."
            }
        }
        
        if case['question_type'] == 'method':
            template = method_descriptions[case['method']]
            premise = template['premise'].format(
                objA=case['objects'][0],
                attrs=', '.join(case['common_attrs'] + [case['derived_attr']]),
                objB=case['objects'][1],
                common_attrs=', '.join(case['common_attrs'])
            )
            conclusion = template['conclusion'].format(
                objB=case['objects'][1],
                derived_attr=case['derived_attr']
            )
            
            return f"""{premise}
{conclusion}

Which method of reasoning does this argument follow?
A. Ψ Method (shared attributes lead to positive conclusion)
B. ⌘ Method (missing attributes lead to negative conclusion)

Please answer with [[A]] or [[B]]."""
        
        else:
            template = method_descriptions[case['method']]
            premise = template['premise'].format(
                objA=case['objects'][0],
                attrs=', '.join(case['common_attrs'] + [case['derived_attr']]),
                objB=case['objects'][1],
                common_attrs=', '.join(case['common_attrs'])
            )
            role_map = {
                'Ψ': {'A': '#Ψ attribute (shared)', 'B': '+Ψ attribute (inferred)'},
                '⌘': {'A': '-⌘ attribute (missing)', 'B': '+⌘ attribute (excluded)'}
            }
            roles = role_map[case['method']]
            
            rule = "There are two types of analogical reasoning:\n\n1. Ψ Method:\n    Object A has attributes a, b, c, d;\n    Object B has attributes a, b, c;\n    Therefore, Object B also has attribute d.\n    Here, attributes a, b, c are referred to as #Ψ attributes, and d is referred to as the +Ψ attribute.\n    \n2. ⌘ Method: \n    Object A has attributes a, b, c, d;\n    Object B does not have attributes a, b, c;\n    Therefore, Object B also does not have attribute d.\n    Here, attributes a, b, c are referred to as -⌘ attributes, and d is referred to as the +⌘ attribute."
            
            
            return random.choice([rule,'']) + f"""In the following example:{premise}
"{case['target_attr']}" is which type of attribute?
A. {roles['A']}
B. {roles['B']}

Please answer with [[A]] or [[B]].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

