import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class KorlogicepistemiclogicInstructionGenerator(BaseInstructionGenerator):
    """Korlogicepistemiclogic Bootcamp指令生成器"""
    
    def __init__(self, names=None, propositions=None, groups=None):
        """
        初始化Korlogicepistemiclogic指令生成器
        
        Args:
            names: 参数描述
            propositions: 参数描述
            groups: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.names = names or ['Alice', 'Bob', 'Charlie']
        self.propositions = propositions or [
            '太阳从东方升起', '2+2=4', '图书馆今天开放', 
            '地球是圆的', '水在0℃结冰', '人类需要氧气'
        ]
        self.groups = groups or ['G', 'GroupA', 'GroupB']
        self.templates = self._load_templates()
    
    def case_generator(self):
        template = random.choice(self.templates)
        return self._fill_template(template)
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rule_desc = KorLogicEpistemicLogicbootcamp.RULE_DESCRIPTIONS.get(question_case["axiom"], "")
        prompt = f"{rule_desc}\n\n{question_case['scenario']}\n"
        
        if question_case["type"] == "multiple_choice":
            prompt += "\n请选择正确的结论：\n" + "\n".join(question_case["options"])
            prompt += "\n\n请将答案用大写字母放在双括号内，例如[[A]]。"
        elif question_case["type"] == "expression":
            prompt += "\n请将逻辑表达式（使用命题符号，无需自然语言）放在双括号内，例如[[G_p ∧ H_Alice_p]]。"
        
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _load_templates(self):
        return [
            # 信念公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Belief",
                "template": {
                    "scenario": "根据信念公理，如果{name}坚信{proposition}（B_{name}({proposition})），我们可以得出以下哪个结论？",
                    "options": [
                        {"text": "{name}可能怀疑{proposition}。", "is_correct": False},
                        {"text": "{proposition}是真实的。", "is_correct": True},
                        {"text": "{name}不知道{proposition}。", "is_correct": False}
                    ]
                }
            },
            # 自反性公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Reflexivity",
                "template": {
                    "scenario": "根据自反性公理，如果{name}坚信某个命题是真的，这意味着什么？",
                    "options": [
                        {"text": "{name}可能对该命题产生怀疑。", "is_correct": False},
                        {"text": "{name}确信自己坚信这个命题。", "is_correct": True},
                        {"text": "{name}和其他人全都知道这个命题。", "is_correct": False}
                    ]
                }
            },
            # 传递性公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Transitivity",
                "requires_two_names": True,
                "template": {
                    "scenario": "根据传递性公理，如果{name1}可以识别{name2}的信念状态（{name1}R{name2}），并且{name1}坚信{proposition}（B_{name1}({proposition})），那么{name2}对该命题的态度是什么？",
                    "options": [
                        {"text": "{name2}可能怀疑该命题。", "is_correct": False},
                        {"text": "{name2}坚信该命题。", "is_correct": True},
                        {"text": "{name2}的态度无法确定。", "is_correct": False}
                    ]
                }
            },
            # 共同信念选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Common Belief",
                "template": {
                    "scenario": "如果命题{proposition}是群体{group}的共同信念，这意味着什么？",
                    "options": [
                        {"text": "{group}中的每个成员都坚信{proposition}。", "is_correct": True},
                        {"text": "只有部分成员坚信{proposition}。", "is_correct": False},
                        {"text": "{group}的成员都怀疑{proposition}。", "is_correct": False}
                    ]
                }
            },
            # 怀疑引入公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Doubt Introduction",
                "template": {
                    "scenario": "根据怀疑引入公理，如果{name}怀疑{proposition}（H_{name}({proposition})），这意味着什么？",
                    "options": [
                        {"text": "{name}坚信{proposition}。", "is_correct": False},
                        {"text": "{name}不坚信{proposition}。", "is_correct": True},
                        {"text": "{name}知道{proposition}是假的。", "is_correct": False}
                    ]
                }
            },
            # 共同信念表达式模板
            {
                "type": "expression",
                "axiom": "Common Belief",
                "template": {
                    "scenario": "如果命题{proposition}是群体{group}的共同信念，但个体{name}怀疑该命题，根据共同信念的定义，对应的逻辑表达式是什么？",
                    "correct_expression": "G_{proposition} ∧ H_{name}_{proposition}"
                }
            },
            # 自反性公理表达式模板
            {
                "type": "expression",
                "axiom": "Reflexivity",
                "template": {
                    "scenario": "如果{name}确信{proposition}（B_{name}({proposition})），并且根据自反性公理确信自己确信此事，对应的逻辑表达式是什么？",
                    "correct_expression": "B_{name}_{proposition} ∧ B_{name}(B_{name}_{proposition})"
                }
            }
        ]

    def _fill_template(self, template):
        params = {}

        # 处理需要两个不同名字的情况
        if template.get('requires_two_names', False):
            names = random.sample(self.names, 2)
            params['name1'] = names[0]
            params['name2'] = names[1]
        else:
            params['name'] = random.choice(self.names)

        params['proposition'] = random.choice(self.propositions)
        params['group'] = random.choice(self.groups)

        filled = {
            "type": template["type"],
            "axiom": template["axiom"],
            "scenario": template["template"]["scenario"].format(**params)
        }

        if template["type"] == "multiple_choice":
            options = []
            correct_answer = None
            for idx, opt in enumerate(template["template"]["options"]):
                option_text = opt["text"].format(**params)
                letter = chr(65 + idx)
                options.append(f"{letter}. {option_text}")
                if opt["is_correct"]:
                    correct_answer = letter
            filled["options"] = options
            filled["correct_answer"] = correct_answer
        elif template["type"] == "expression":
            filled["correct_expression"] = template["template"]["correct_expression"].format(**params).replace(" ", "")

        return filled
