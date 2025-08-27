"""### 谜题描述
Time Propositions:
1. Symbol \"H\" represents \"past point in time\".
2. Symbol \"A\" represents \"past period of time\".
3. Symbol \"F\" represents \"future point in time\".
4. Symbol \"G\" represents \"future period of time\".
5. Symbol \"T\" represents \"present\".

Time Proposition Relationships:
(1) ※ Relationship:
- Pairs: Ap and H¬p; A¬p and Hp; Gp and F¬p; G¬p and Fp
- Properties: They cannot both be true, nor both false.

(2) ↦ Relationship:
- Pairs: Ap and A¬p; Gp and G¬p
- Properties: They cannot both be true, but can both be false.

(3) ⚭ Relationship:
- Pairs: Hp and H¬p; Fp and F¬p
- Properties: They cannot both be false, but can both be true.

(4) ⁂ Relationship:
- Pairs: Ap and Hp, A¬p and H¬p; Gp and Fp, G¬p and F¬p
- Properties: They can both be true, or both be false.

Time Proposition Inference Formulas:
(1) Ap ↔ H¬p
(2) A¬p ↔ ¬Hp
(3) Hp ↔ ¬A¬p
(4) H¬p ↔ ¬Ap
(5) Ap → ¬A¬p
(6) A¬p → ¬Ap
(7) ¬Hp → H¬p
(8) ¬H¬p → Hp
(9) Ap → Hp
(10) A¬p → H¬p
(11) ¬Hp → ¬Ap
(12) ¬H¬p → ¬A¬p
(13) Gp ↔ F¬p
(14) G¬p ↔ ¬Fp
(15) Fp ↔ ¬G¬p
(16) F¬p ↔ ¬Gp
(17) Gp → ¬G¬p
(18) G¬p → ¬Gp
(19) ¬Fp → F¬p
(20) ¬F¬p → Fp
(21) Gp → Fp
(22) G¬p → F¬p
(23) ¬Fp → ¬Gp
(24) ¬F¬p → ¬G¬pExample questions are as follows:

<example 0>
Symbolize the following propositions:
(1) Wang Qiang worked in Beijing for one year in the past.
(2) Lin Min has lived in Ningbo in the past.

Use p to represent the ordinary propositions.

Please provide the answers in the format [[];[]].
</example 0>

<example 1>
Symbolize the following propositions:
(1) Xiao Jin will go to England to study abroad next year.
(2) Xiao Qian will permanently settle in England.

Use p to represent the ordinary propositions.

Please provide the answers in the format [[];[]].
</example 1>

<example 2>
What relationships do the following sentences have?

(1) \"Old Li's health was good in the past\" and \"At some point in the past, Old Li's health was not very good\"
(2) \"Aunt Wang never won a major award in the past\" and \"Allow the execution of contracts\"

A. ※ Relationship       B. ↦ Relationship     C. ⚭ Relationship    D. ⁂ Relationship

Please provide the answer in the format [[A/B/C/D];[A/B/C/D]].
</example 2>

<example 3>
What relationships do the following sentences have?

(1) \"Xiao Lin will win the computer competition championship trophy\" and \"It is not true that Xiao Lin will never win the computer competition championship trophy\"
(2) \"Xiao Bai will permanently settle in the United States\" and \"Xiao Bai will settle in the United States\"

A. ※ Relationship       B. ↦ Relationship     C. ⚭ Relationship    D. ⁂ Relationship

Please provide the answer in the format [[A/B/C/D];[A/B/C/D]].
</example 3>

<example 4>
\"Old Zhao did not work in Ningbo at some point in the past\" can be inferred from \"It is not the case that Old Zhao worked in Ningbo all the time in the past.\" 
Conversely, \"It is not the case that Old Zhao worked in Ningbo all the time in the past\" can be inferred from \"Old Zhao did not work in Ningbo at some point in the past.\"

Which reasoning formulas does this correspond to?

Please give your answer in [[number]] format.
</example 4>

<example 5>
\"Dr Lee has been working on farms in the past\" leads to: \"Dr Lee has been working on farms at some time in the past\".

Which of these correspond to the inference formulae?

Please give your answer in [[number]] format.
</example 5>

<example 6>
According to reasoning formula 5, what can be inferred from \"Lao Chen has always worked diligently in the past\"?

A.It is not that Mr Chan has not been working seriously in the past.
B. Mr Chen has always been serious about his work in the future.
C. Mr Chen will start working seriously in March next year.
D. Mr Chan has not been working seriously in the past.

Please provide the answer in the format [[A/B/C/D]].
</example 6>

<example 7>
According to Reasoning Equation 21, what can be deduced from \"I will always keep on painting\"?

A. I used to stick to painting.
B. I keep on painting.
C. I will start painting tomorrow.
D. I will keep on painting.

Please provide the answer in the format [[A/B/C/D]].
</example 7>

<example 8>
Reasoning Formula 7 is consistent with what following what relationship?

A. ∗ relationship 
B. ↦ relationship 
C. ⚭ relationship 
D. ⁂ relationship

Please provide the answer in the format [[A/B/C/D]].
</example 8>

<example 9>
Reasoning Formula 17 is consistent with what following what relationship?

A. ∗ relation 
B. ↦ relation 
C. ⚭ relation 
D. ⁂ relation

Please provide the answer in the format [[A/B/C/D]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
import re

class KorLogicTemporalPropositionsbootcamp(Basebootcamp):
    def __init__(self, **params):
        default_params = {
            'symbolize_prob': 0.5,
            'relationship_prob': 0.5,
            'action_words': ['work in Beijing', 'have good health', 'study abroad', 'settle permanently'],
            'subjects': ['Wang Qiang', 'Lin Min', 'Xiao Jin', 'Old Zhao', 'Dr Lee']
        }
        self.params = {**default_params, **params}
        
    def case_generator(self):
        case_type = random.choices(
            ['symbolize', 'relationship'],
            weights=[
                self.params['symbolize_prob'],
                self.params['relationship_prob'],
            ],
            k=1
        )[0]

        if case_type == 'symbolize':
            return self._generate_symbolize_case()
        elif case_type == 'relationship':
            return self._generate_relationship_case()
        else:
            raise ValueError(f'Invalid case type: {case_type}')

    def _generate_symbolize_case(self):
        symbols = ['A', 'H']
        negation = ['', '¬']
        propositions = []
        answers = []
        
        for _ in range(2):
            sym = random.choice(symbols)
            neg = random.choice(negation)
            p = f"{sym}{neg}p"
            propositions.append(self._symbol_to_sentence(p))
            answers.append(p)
        
        return {
            'type': 'symbolize',
            'propositions': propositions,
            'answers': answers
        }

    def _generate_relationship_case(self):
        rel_defs = [
            ('※', [('Ap', 'H¬p'), ('Gp', 'F¬p')], 'A'),
            ('↦', [('Ap', 'A¬p'), ('Gp', 'G¬p')], 'B'),
            ('⚭', [('Hp', 'H¬p'), ('Fp', 'F¬p')], 'C'),
            ('⁂', [('Ap', 'Hp'), ('Gp', 'Fp')], 'D')
        ]
        rel_type = random.choice(rel_defs)
        pairs = [random.choice(rel_type[1]) for _ in range(2)]
        
        return {
            'type': 'relationship',
            'pairs': [(self._symbol_to_sentence(p[0]), self._symbol_to_sentence(p[1])) for p in pairs],
            'correct_options': [rel_type[2]]*2
        }

    def _generate_formula_inference_case(self):
        formula_map = [
            (7, '¬Hp', 'H¬p'),
            (8, '¬H¬p', 'Hp'),
            (21, 'Gp', 'Fp')
        ]
        formula = random.choice(formula_map)
        return {
            'type': 'formula_inference',
            'premise': self._symbol_to_sentence(formula[1]),
            'conclusion': self._symbol_to_sentence(formula[2]),
            'correct_formula': formula[0]
        }

    def _symbol_to_sentence(self, symbol):
        subject = random.choice(self.params['subjects'])
        action = random.choice(self.params['action_words'])
        base = {
            'Ap': f"{subject} always {action}ed in the past",
            'A¬p': f"{subject} never {action}ed during the entire past period",
            'Hp': f"At some point in the past, {subject} {action}ed",
            'H¬p': f"At some point in the past, {subject} did not {action}",
            'Gp': f"{subject} will {action} permanently in the future",
            'G¬p': f"{subject} will not {action} permanently in the future",
            'Fp': f"Next year, {subject} will {action}",
            'F¬p': f"In the future, {subject} will not {action}",
            '¬Hp': f"It is not true that {subject} {action}ed at some past time",
            '¬H¬p': f"It is not true that {subject} did not {action} at some past time"
        }
        return base.get(symbol, "Invalid symbol")

    @staticmethod
    def prompt_func(question_case):
        if question_case['type'] == 'symbolize':
            prompt = """Time Proposition Symbolization Rules:
1. H: Past point in time (e.g., "at some point")
2. A: Past period of time (e.g., "throughout the past")
3. F: Future point in time
4. G: Future period of time
5. T: Present (not used in these examples)

Symbolize these propositions:
"""
            for i, p in enumerate(question_case['propositions'], 1):
                prompt += f"({i}) {p}\n"
            prompt += "\nFormat your answer as [[symbol1];[symbol2]]"
            return prompt
        
        elif question_case['type'] == 'relationship':
            prompt = """Relationship Types:
※: Cannot be both true nor both false
↦: Cannot both be true but can both be false
⚭: Cannot both be false but can both be true
⁂: Can both be true or both be false

Analyze these pairs:
"""
            for i, (p1, p2) in enumerate(question_case['pairs'], 1):
                prompt += f"({i}) '{p1}' vs '{p2}'\n"
            prompt += "Options:\nA. ※\nB. ↦\nC. ⚭\nD. ⁂\nAnswer format: [[A/B/C/D];[A/B/C/D]]"
            return prompt
        
        else:
            prompt = f"""Given the inference rule:
Premise: {question_case['premise']}
Conclusion: {question_case['conclusion']}

Which inference formula number does this correspond to? Answer with [[number]]"""
            return prompt

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1]
        return [x.strip() for x in last_match.split(';')]

    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['type'] == 'symbolize':
            return solution == identity['answers']
        elif identity['type'] == 'relationship':
            return solution == identity['correct_options']
        elif identity['type'] == 'formula_inference':
            return solution == [str(identity['correct_formula'])]
        return False
    
if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicTemporalPropositionsbootcamp
        bootcamp = KorLogicTemporalPropositionsbootcamp()
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
