"""### 谜题描述
Symbol Definitions:
- Belief (`B_p`): Indicates that an individual firmly believes the proposition `p` is true.
- Common Belief (`G_p`): Indicates that the proposition `p` is a common belief within the group `G`, meaning all members collectively believe `p`.
- Doubt (`H_p`): Indicates that an individual harbors doubt about the truth of the proposition `p`.

Cognitive Logic Model:
Cognitive logic simulates the interaction between different worlds and beliefs through the construction of models:
- Model (`M`): Composed of three parts:
    - Set of Worlds (`W`): All possible worlds.
    - Accessibility Relation (`R`): If `iRj`, it means individual `i` can recognize the belief state of individual `j`.
    - Truth Value Function of Propositions (`V`): Defines the truth value of each proposition in each world.

Definition of Common Belief:
If `p` is a common belief in the group `G`, then for every member `i` of the group, `B_ip` holds.

Cognitive Logic Axioms:

1. Basic Axioms
- Belief Axiom: `B_p → p`, indicating that if someone firmly believes `p` is true, it can be inferred that `p` is indeed true.

2. Advanced Axioms
- Axiom of Reflexivity: `B_p → BB_p`, indicating that if an individual firmly believes the proposition `p`, they also believe they believe `p`.
- Axiom of Transitivity: If `iRj` and `B_ip`, then `B_jp`, indicating that if individual `i` firmly believes the proposition `p` and can recognize individual `j`, then `j` also believes `p`.
- Axiom of Consistent Belief: `B_p ∧ B_{¬p} → ⊥`, indicating that an individual cannot simultaneously believe in a proposition `p` and its negation `¬p`, as this would lead to a logical contradiction.

3. Axioms of Doubt
- Introduction of Doubt: `H_p → ¬B_p`, indicating that if an individual doubts the proposition `p`, they do not firmly believe `p`.
- Spread of Doubt: If `iRj` and `H_ip`, then `H_jp`, indicating that if individual `i` doubts the proposition `p` and can recognize individual `j`, then `j` may also start to doubt `p`.Example questions are as follows:

<example 0>
Based on the Belief Axiom, if Alice firmly believes that the sun rises in the east (`B_Alice(The sun rises in the east)`), we can conclude the following:

A. Alice may doubt that the sun rises in the east.
B. It is true that the sun rises in the east.
C. Alice is unaware that the sun rises in the east.

Please provide the answers in the format [[A/B/C]].
</example 0>

<example 1>
According to the Axiom of Reflexivity, what does it mean if Alice firmly believes a certain proposition to be true?

A. Alice may have doubts about this proposition.
B. Alice is convinced that she herself is convinced of this proposition.
C. Alice and other people are all aware of this proposition.

Please provide the answers in the format [[A/B/C]].
</example 1>

<example 2>
If both Alice and Bob firmly believe that 2 plus 2 equals 4, according to the definition of common belief, what does this mean?

A. Alice and Bob both know that 2 plus 2 equals 4.
B. Only Alice firmly believes that 2 plus 2 equals 4.
C. Bob doubts that 2 plus 2 equals 4.

Please provide the answers in the format [[A/B/C]].
</example 2>

<example 3>
According to the Axiom of Transitivity, if Alice is certain that Bob is certain of a certain proposition, and Alice is also certain of this proposition, what is Bob's attitude towards this proposition?

A. Bob might suspect this proposition.
B. Bob is convinced of this proposition.
C. Bob's attitude towards this proposition is uncertain.

Please provide the answers in the format [[A/B/C]].
</example 3>

<example 4>
According to the Axiom of Consistent Belief, what does it mean if Alice firmly believes in a proposition and its negation at the same time?

A. Alice's beliefs are coherent.
B. There exists an inconsistency within Alice's beliefs.
C. This scenario is not possible.

Please provide the answers in the format [[A/B/C]].
</example 4>

<example 5>
If Alice harbors doubts that the library is open today, what is Alice convinced of according to the Introduction of Doubt axiom?

A. That the library is open today.
B. That the library is not open today.
C. That she is not certain whether the library is open today.

Please provide the answers in the format [[A/B/C]].
</example 5>

<example 6>
If Alice is skeptical about the library being open today, and Bob can acknowledge Alice's skepticism, what is Bob likely to be convinced of, based on the Spread of Doubt axiom?

A. That the library is open today.
B. That the library is closed today.
C. That he may also begin to doubt whether the library is open today.

Please provide the answers in the format [[A/B/C]].
</example 6>

<example 7>
If there exists an accessibility relation between Alice and Bob, and Alice harbors doubts about a certain proposition, what is Bob likely to be convinced of, based on the Spread of Doubt axiom?

A. That the proposition is true.
B. That the proposition is false.
C. That he might also harbor doubts about the proposition.

Please provide the answers in the format [[A/B/C]].
</example 7>

<example 8>
If a proposition p is the consensus of the group G, 
but the individual Alice doubts this proposition, 
what logical expression can be written according to the definition of consensus?

Please give your answer in the format [[]].
</example 8>

<example 9>
If Alice is sure that the library is open today (proposition p), 
and she is sure that she is sure of this (according to the axiom of self-reflexivity), 
what logical expression is written?

Please give your answer in the format [[]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from bootcamp import Basebootcamp

class KorLogicEpistemicLogicbootcamp(Basebootcamp):
    RULE_DESCRIPTIONS = {
        "Belief": "信念公理（Belief Axiom）：如果某人坚信命题p成立（B_p），那么p是真实的。",
        "Reflexivity": "自反性公理（Axiom of Reflexivity）：如果某人坚信命题p（B_p），那么他也坚信自己坚信p（BB_p）。",
        "Transitivity": "传递性公理（Axiom of Transitivity）：如果个体i可以识别个体j的信念状态（iRj），并且i坚信命题p（B_i p），那么j也将坚信p（B_j p）。",
        "Common Belief": "共同信念定义（Common Belief）：如果命题p是群体G的共同信念（G_p），那么群体内的每个成员都坚信p。",
        "Consistent Belief": "一致性信念公理（Axiom of Consistent Belief）：个体不能同时相信命题p及其否定¬p，否则会导致逻辑矛盾。",
        "Doubt Introduction": "怀疑引入公理（Introduction of Doubt）：如果个体怀疑命题p（H_p），则他不坚信p（¬B_p）。",
        "Doubt Spread": "怀疑传播公理（Spread of Doubt）：如果个体i可以识别j的信念状态（iRj）且i怀疑p（H_i p），则j也怀疑p（H_j p）。"
    }
    
    def __init__(self, names=None, propositions=None, groups=None):
        super().__init__()
        self.names = names or ['Alice', 'Bob', 'Charlie']
        self.propositions = propositions or [
            '太阳从东方升起', '2+2=4', '图书馆今天开放', 
            '地球是圆的', '水在0℃结冰', '人类需要氧气'
        ]
        self.groups = groups or ['G', 'GroupA', 'GroupB']
        self.templates = self._load_templates()

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

    def case_generator(self):
        template = random.choice(self.templates)
        return self._fill_template(template)

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

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
            
        if identity["type"] == "multiple_choice":
            return solution.upper() == identity["correct_answer"]
        elif identity["type"] == "expression":
            # 标准化比较：移除所有空格
            return solution.replace(" ", "") == identity["correct_expression"]
        return False
