"""### 谜题描述
Custom Formal Fallacy Naming Rules:
- NegAnt Method: If P, then Q. Not P, erroneously concludes Not Q.
- AffCons Method: If P, then Q. Q is true, erroneously concludes P.
- CondSwap Method: If P then Q, erroneously believes that if Q then P.
- IncorrNeg Method: If P then Q, erroneously concludes that if Not P then Not Q.
- DisjSyl Method: Either P or Q. Knowing Q, erroneously concludes Not P.
- QuantSwitch Method: ∀x∃y R(x, y), therefore, ∃y∀x R(x, y). Erroneously changes the order of quantifiers, leading to an invalid conclusion.
- IllTrans Method: ∀x (Sx → Px), therefore, ∀x (Px → Sx). It is erroneous to infer \"all P are S\" from \"all S are P\". Similarly, from ∃x (Sx ∧ ¬Px), it is erroneous to infer ∃x (Px ∧ ¬Sx). Erroneously converts the terms in the proposition, leading to an invalid conclusion.
- IncorrInf Method: From ∃x (Sx ∧ Px) infer ∃x (Sx ∧ ¬Px), and from ∃x (Sx ∧ ¬Px) infer ∃x (Sx ∧ Px). It is erroneous to infer \"some S are not P\" from \"some S are P\" and vice versa. An invalid inference is made about propositions with existential quantifiers.
- InvSubError Method: `K(x, y)` indicates that individual x knows that y is true. `R(x, y, z)` indicates that x has a relationship z with y. `SubError(x, y, z)` indicates a substitution error when incorrectly applying knowledge or attributes about y to z.
- LetClauseShift Method: When the structure of a statement is incorrectly adjusted or interpreted, causing the original intent or logical relationship to be misrepresented. For example, a shift in the structure of a let clause leads to an invalid inference.Example questions are as follows:

<example 0>
If Li Gua murdered his boss, then he is an evil person. Li Gua did not murder his boss, so Li Gua is not an evil person. This reasoning is obviously unsound. The act of murder (regardless of whether it is the boss) can indeed make a person an evildoer, but evildoers are not limited to murderers; there are many other forms of wrongdoing. Therefore, it cannot be concluded that \"Li Gua is not an evil person\" from \"Li Gua did not murder someone.\"

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 0>

<example 1>
If Wang Meng is an internet enthusiast, then he will spend a long time online. Wang Meng does indeed spend a long time online, so Wang Meng must be an internet enthusiast. This reasoning is invalid. Even if the premises are true, the conclusion can be false. For example, Wang Meng spends a long time online because it is his job. He has started to hate his job because he is always dealing with the virtual world of the internet, which has made him a bit confused about reality and truth, losing a sense of security, and not as real and substantial as interacting with real people.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 1>

<example 2>
If x is a positive even number, then x is a natural number, so, if x is a natural number, then x is a positive even number. Everyone who has been to elementary school understands that this reasoning is incorrect.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 2>

<example 3>
If all countries in the Middle East disarm, it will bring peace to the region, so if the countries in the Middle East have not disarmed, there will be no peace in the region. The premise is true, but the conclusion is obviously not valid, because it is impossible for all countries in the Middle East to completely disarm. According to this conclusion, there will never be peace in the Middle East, but the real situation will not be so.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 3>

<example 4>
Du Fu is either a great poet or a person from the Tang Dynasty, and Du Fu is a world-renowned great poet, so Du Fu is not a person from the Tang Dynasty. Since the disjunctive proposition as the premise is compatible, each branch proposition can be true at the same time, this reasoning is incorrect.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 4>

<example 5>
Considering the domain of individuals as natural numbers and R representing the \"less than\" relationship, ∀x∃yR(x, y) states that for any natural number, you can find another natural number greater than it, meaning there is no largest natural number. However, ∃y∀xR(x, y) suggests that there is a natural number greater than any other natural number, implying the existence of a largest natural number. Here, the premise is true, but the conclusion is false, making the reasoning invalid.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 5>

<example 6>
\"All Chinese billionaires are Chinese people,\" so \"all Chinese people are Chinese billionaires.\" The premise is true, but the conclusion is false, making the reasoning invalid.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 6>

<example 7>
Given: Some students are doctors. Erroneous inference: Therefore, some students are not doctors.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 7>

<example 8>
Xiao Qiang knows that Lu Xun is Lu Xun, and Lu Xun is the brother of the biologist Zhou Jianren, so Xiao Qiang knows that Lu Xun is the brother of the biologist Zhou Jianren. This reasoning is invalid; it incorrectly infers a proposition about Xiao Qiang's knowledge from a proposition in the real world, creating a logical fallacy.

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 8>

<example 9>
Suppose a company manager (let's call him Manager M) announces a new policy: \"All employees (E) will receive a bonus (B) after completing a project (P).\" However, an employee (let's call him Employee A) misunderstands this statement, thinking that \"only when an employee receives a bonus (B) have they completed a project (P).\"

What type of formal fallacy is this?

A. NegAnt Method
B. AffCons Method
C. CondSwap Method
D. IncorrNeg Method
E. DisjSyl Method
F. QuantSwitch Method
G. IllTrans Method
H. IncorrInf Method
I. InvSubError Method
J. LetClauseShift Method

Please give your answer in the format [[A/B/C/D/E/F/G/H/I/J]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
from collections import OrderedDict

class KorLogicFormalFallaciesbootcamp(Basebootcamp):
    def __init__(self, **params):
        self.fallacy_map = OrderedDict([
            ('A', 'NegAnt Method'),
            ('B', 'AffCons Method'),
            ('C', 'CondSwap Method'),
            ('D', 'IncorrNeg Method'),
            ('E', 'DisjSyl Method'),
            ('F', 'QuantSwitch Method'),
            ('G', 'IllTrans Method'),
            ('H', 'IncorrInf Method'),
            ('I', 'InvSubError Method'),
            ('J', 'LetClauseShift Method')
        ])
        self.params = params
        
    def case_generator(self):
        correct_key = random.choice(list(self.fallacy_map.keys()))
        question_text, analysis = self.generate_question(correct_key)
        return {
            'question': question_text,
            'analysis': analysis,
            'correct_answer': correct_key,
            'options': self.fallacy_map.copy()
        }

    def generate_question(self, key):
        generators = {
            'A': self._gen_negant,
            'B': self._gen_affcons,
            'C': self._gen_condswap,
            'D': self._gen_incorrneg,
            'E': self._gen_disjsyl,
            'F': self._gen_quantswitch,
            'G': self._gen_illtrans,
            'H': self._gen_incorrinf,
            'I': self._gen_invsuberror,
            'J': self._gen_letclauseshift
        }
        return generators[key]()

    # 实现所有缺失的生成方法
    def _gen_negant(self):
        templates = [
            ("If {A} then {B}. Not {A}, therefore not {B}.", 
            "否定前件错误：通过否定条件命题的前件来错误否定后件")
        ]
        return self._fill_template(templates, 
            {'A': ['P', 'Q', 'X'], 'B': ['Q', 'R', 'Y']})

    def _gen_affcons(self):
        templates = [
            ("If {A} then {B}. {B} is true, so {A} must be true.",
            "肯定后件错误：通过肯定条件命题的后件来错误肯定前件")
        ]
        return self._fill_template(templates,
            {'A': ['P', 'Q'], 'B': ['Q', 'R']})

    def _gen_condswap(self):
        templates = [
            ("If {A} then {B}, therefore if {B} then {A}.",
            "条件倒置错误：错误交换条件命题的前后件")
        ]
        return self._fill_template(templates,
            {'A': ['P', 'Q'], 'B': ['Q', 'R']})

    def _gen_incorrneg(self):
        templates = [
            ("If {A} then {B}, therefore if ¬{A} then ¬{B}.",
            "错误否定推演：错误地将原命题的否定作为结论")
        ]
        return self._fill_template(templates,
            {'A': ['P', 'Q'], 'B': ['Q', 'R']})

    def _gen_disjsyl(self):
        templates = [
            ("Either {A} or {B}. {B} is true, so {A} is false.",
            "析取谬误：错误否定相容析取命题的另一选项")
        ]
        return self._fill_template(templates,
            {'A': ['P', 'X'], 'B': ['Q', 'Y']})

    def _gen_quantswitch(self):
        templates = [
            ("∀x∃y R(x,y) therefore ∃y∀x R(x,y)",
            "量词换序错误：错误交换全称量词和存在量词的位置")
        ]
        return random.choice(templates)

    def _gen_illtrans(self):
        templates = [
            ("All {S} are {P}, therefore all {P} are {S}.",
            "非法换位：错误转换全称命题的主谓项位置")
        ]
        elements = {'S': ['S', 'A'], 'P': ['P', 'B']}
        return self._fill_template(templates, elements)

    def _gen_incorrinf(self):
        templates = [
            ("Some {S} are {P}, therefore some {S} are not {P}.",
            "存在量词谬误：错误转换存在命题的肯定与否定")
        ]
        return self._fill_template(templates,
            {'S': ['S', 'A'], 'P': ['P', 'B']})

    def _gen_invsuberror(self):
        templates = [
            ("Knowing {X} is {Y}, therefore {X} knows {Z}.",
            "无效替换错误：错误替换认知命题中的嵌套内容")
        ]
        return self._fill_template(templates, {
            'X': ['A', 'B'], 
            'Y': ['P', 'Q'], 
            'Z': ['R', 'S']
        })

    def _gen_letclauseshift(self):
        templates = [
            ("Original statement: {A}, Misinterpretation: {B}",
            "条款结构篡改：错误解释逻辑连接词的辖域范围")
        ]
        return self._fill_template(templates, {
            'A': ["∀x(P(x)→Q(x))", "∃x(S(x)∧T(x))"],
            'B': ["∀x(P(x)∧Q(x))", "∃x(S(x)→T(x))"]
        })

    def _fill_template(self, templates, elements):
        template, analysis = random.choice(templates)
        filled = template.format(**{
            k: random.choice(v) for k, v in elements.items()
        })
        return filled, analysis

    @staticmethod
    def prompt_func(question_case) -> str:
        
        rule = "Custom Formal Fallacy Naming Rules:\n- NegAnt Method: If P, then Q. Not P, erroneously concludes Not Q.\n- AffCons Method: If P, then Q. Q is true, erroneously concludes P.\n- CondSwap Method: If P then Q, erroneously believes that if Q then P.\n- IncorrNeg Method: If P then Q, erroneously concludes that if Not P then Not Q.\n- DisjSyl Method: Either P or Q. Knowing Q, erroneously concludes Not P.\n- QuantSwitch Method: ∀x∃y R(x, y), therefore, ∃y∀x R(x, y). Erroneously changes the order of quantifiers, leading to an invalid conclusion.\n- IllTrans Method: ∀x (Sx → Px), therefore, ∀x (Px → Sx). It is erroneous to infer \"all P are S\" from \"all S are P\". Similarly, from ∃x (Sx ∧ ¬Px), it is erroneous to infer ∃x (Px ∧ ¬Sx). Erroneously converts the terms in the proposition, leading to an invalid conclusion.\n- IncorrInf Method: From ∃x (Sx ∧ Px) infer ∃x (Sx ∧ ¬Px), and from ∃x (Sx ∧ ¬Px) infer ∃x (Sx ∧ Px). It is erroneous to infer \"some S are not P\" from \"some S are P\" and vice versa. An invalid inference is made about propositions with existential quantifiers.\n- InvSubError Method: `K(x, y)` indicates that individual x knows that y is true. `R(x, y, z)` indicates that x has a relationship z with y. `SubError(x, y, z)` indicates a substitution error when incorrectly applying knowledge or attributes about y to z.\n- LetClauseShift Method: When the structure of a statement is incorrectly adjusted or interpreted, causing the original intent or logical relationship to be misrepresented. For example, a shift in the structure of a let clause leads to an invalid inference.\n"
        
        options = "\n".join([f"{k}. {v}" for k, v in question_case['options'].items()])
        return rule + f"""请分析以下逻辑谬误类型：

{question_case['question']}

备选类型：
{options}

请将答案用双括号包裹，例如[[A]]。"""

    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[([A-J])]]', output)
        return matches[-1].upper() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return solution == identity['correct_answer']
        except:
            return False
        
if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicFormalFallaciesbootcamp
        bootcamp = KorLogicFormalFallaciesbootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break
