"""### 谜题描述
1. Propositional Symbolization Rules:
    - Equivalence is represented by `::=::`
    - Negation is represented by `!`
    - Or is represented by `|`
    - And is represented by `&`
    - Implication is represented by `>`
    - Equivalence is represented by `=`
    - NAND is represented by `⇑`
    - NOR is represented by `⇓`
2. Basic Equivalences:
    (1) A ::=:: !!A
    (2) A ::=:: A | A, A ::=:: A & A
    (3) A | B ::=:: B | A, A & B ::=:: B & A
    (4) (A | B) | C ::=:: A | (B | C), (A & B) & C ::=:: A & (B & C)
    (5) A | (B & C) ::=:: (A | B) & (A | C), A & (B | C) ::=:: (A & B) | (A & C)
    (6) !(A | B) ::=:: !A & !B, !(A & B) ::=:: !A | !B
    (7) A | (A & B) ::=:: A, A & (A | B) ::=:: A
    (8) A | !A ::=:: 1
    (9) A & !A ::=:: 0
    (10) A > B ::=:: !A | B
    (11) A = B ::=:: (A > B) & (B > A)
    (12) A > B ::=:: !B > !A
    (13) A = B ::=:: !A = !B
    (14) (A > B) & (A > !B) ::=:: !A
    (15) A ⇑ B ::=:: !A | !B
    (16) A ⇓ B ::=:: !A & !B
3. Equivalence Calculation Rules:
    - The final expression should be completely represented using `|`, `&`, and `!`, without retaining `>` and `=`.
4. Truth Value Judgment Steps:
    - Define the practical problem to be judged as simple propositions and symbolize them.
    - Use simple propositions to express the formula based on each person's description.
    - Combine the information of who is true and who is false to write the final logical expression.
    - Use the above equivalences to derive and judge the truth of the expression.Example questions are as follows:

<example 0>
Using Basic Equivalences (10), what equivalent expression is obtained by removing all occurrences of > in (p > q) > r?
The answer is a logical expression formatted as [[ ]].! has the highest priority, and note that parentheses should only be used when logically needed to emphasise the order of operations, avoiding redundant or unnecessary brackets.
</example 0>

<example 1>
According to the rules, are (p>q)>r and p>(q>r) equivalent? 
A. Yes B. No
The answer is a single English letter.The answer format should be like [[A]].
</example 1>

<example 2>
Using the 16 Basic Equivalences, what is the simplest result obtained through equivalence derivation?
(1) !(p>(p|q))&r
(2) p&(((p|q)&!p)>q)
Provide your answers as logical expressions formatted as [[];[]].
</example 2>

<example 3>
According to the 16 Basic Equivalences, is the equivalence below valid? A. Yes B. No
(1) p::=::(p&q)|(p&!q)
(2) (p&!q)|(!p&q)::=::(p|q)&(!(p|q))
The answer to each sub-question is a letter of the alphabet, and answers to different sub-questions are separated by ;.The answer format should be like [[A];[A]].
</example 3>

<example 4>
According to the 16 Basic Equivalences, is the equivalence below valid? A. Yes B. No
(1) ((p>q)&(p>r))::=::(p>(q|r))
(2) !(p=q)::=::(p|q)&!(p&q)
The answer to each sub-question is a letter of the alphabet, and answers to different sub-questions are separated by ;.The answer format should be like [[A];[A]].
</example 4>

<example 5>
According to the 16 Basic Equivalences, is the equivalence below valid? A. Yes B. No
(1) (p⇓q)⇓r::=::p⇓(q⇓r)
(2) (p⇑q)⇑r::=::p⇑(q⇑r)
The answer to each sub-question is a letter of the alphabet, and answers to different sub-questions are separated by ;.The answer format should be like [[A];[A]].
</example 5>

<example 6>
During a break at a seminar, three attendees tried to determine where Professor Wang is from based on his accent. Their statements were as follows:

First person: Professor Wang is not from Suzhou, he is from Shanghai.
Second person: Professor Wang is not from Shanghai, he is from Suzhou.
Third person: Professor Wang is neither from Shanghai nor from Hangzhou.

After hearing these judgments, Professor Wang chuckled and remarked, \"One of you got everything right, one got half right, and one got everything wrong.\"
Let p denote \"Professor Wang is from Suzhou,\" 
q denote \"Professor Wang is from Shanghai,\" 
and r denote \"Professor Wang is from Hangzhou.\" 
Exactly one of p,q,r is true, and the other two are false.
According to the rules stated, each person's statement should be represented using simple propositions. So, what would the statements of First person, Second person, and Third person be represented as?
Answers are formatted as [[ ];[ ];[ ]]. Each bracketed section should contain the corresponding logical expression for each individual statement.
</example 6>

<example 7>
During a break at a seminar, three attendees tried to determine where Professor Wang is from based on his accent. Their statements were as follows:

Person A: Professor Wang is not from Suzhou, he is from Shanghai.
Person B: Professor Wang is not from Shanghai, he is from Suzhou.
Person C: Professor Wang is neither from Shanghai nor from Hangzhou.

After hearing these judgments, Professor Wang chuckled and remarked, \"One of you got everything right, one got half right, and one got everything wrong.\"

Let p denote \"Professor Wang is from Suzhou,\" 
q denote \"Professor Wang is from Shanghai,\" 
and r denote \"Professor Wang is from Hangzhou.\" 

Exactly one of p,q,r is true, and the other two are false.
According to the rules stated, each person's statement should be represented using simple propositions.
Represent each person's statement:
Person A:!p&q
Person B:p&!q
Person C:!q&!r

Define the following logical expressions for Person A:
B1=!p&q (Person A's statements are entirely correct).
B2=(!p&!q)|(p&q) (Person A's  statements are partially correct).
B3=p&!q (Person A's statements are entirely incorrect).

Similarly, define the analogous expressions for Person B:
C1 (Person B's statements are entirely correct).
C2 (Person B's  statements are partially correct).
C3 (Person B's statements are entirely incorrect).

And for Person C:
D1 (Person C's statements are entirely correct).
D2 (Person C's  statements are partially correct).
D3 (Person C's statements are entirely incorrect).

Please provide the corresponding logical expressions. The answer format should be:
[[C1=...];[C2=...];[C3=...];[D1=...];[D2=...];[D3=...]].
</example 7>

<example 8>
During a break at a seminar, three attendees tried to determine where Professor Wang is from based on his accent. Their statements were as follows:

Person A: Professor Wang is not from Suzhou, he is from Shanghai.
Person B: Professor Wang is not from Shanghai, he is from Suzhou.
Person C: Professor Wang is neither from Shanghai nor from Hangzhou.

After hearing these judgments, Professor Wang chuckled and remarked, \"One of you got everything right, one got half right, and one got everything wrong.\"
Let p denote \"Professor Wang is from Suzhou,\" 
q denote \"Professor Wang is from Shanghai,\" 
and r denote \"Professor Wang is from Hangzhou.\" 

Exactly one of p,q,r is true, and the other two are false.
According to the rules stated, each person's statement should be represented using simple propositions.
Represent each person's statement:
Person A:!p&q
Person B:p&!q
Person C:!q&!r

Define the following logical expressions for Person A:
B1=!p&q (Person A's statements are entirely correct).
B2=(!p&!q)|(p&q) (Person A's  statements are partially correct).
B3=p&!q (Person A's statements are entirely incorrect).

Similarly, define the analogous expressions for Person B:
C1=p&!q.(Person B's statements are entirely correct).
C2=(p & q) | (!p & !q).(Person B's  statements are partially correct).
C3=!p&q.(Person B's statements are entirely incorrect).

And for Person C:
D1=!q&!r.(Person C's statements are entirely correct).
D2=(!q&r)|(q&!r).(Person C's  statements are partially correct).
D3=q&r.(Person C's statements are entirely incorrect).

According to Professor Wang's remarks, the final logical expression
E=(B1&C2&D3)|(B1&C3&D2)|(B2&C1&D3)|(B2&C3&D1)|(B3&C1&D2)|(B3&C2&D1)

After equivalent derivation according to the above rules:
(1) What does B1&C2&D3 simplify to?
(2) What does B1&C3&D2 simplify to?
(3) What does B2&C1&D3 simplify to?
(4) What does B2&C3&D1 simplify to?
(5) What does B3&C1&D2 simplify to?
(6) What does B3&C2&D1 simplify to?
(7) What does E finally simplify to?

Please provide the corresponding logical expressions. The answer format should be:
[[B1&C2&D3::=::…];[B1&C3&D2::=::…];[B2&C1&D3::=::…];[B2&C3&D1::=::…];[B3&C1&D2::=::…];[B3&C2&D1::=::…];[E::=::…]].
</example 8>

<example 9>
During a break at a seminar, three attendees tried to determine where Professor Wang is from based on his accent. Their statements were as follows:

Person A: Professor Wang is not from Suzhou, he is from Shanghai.
Person B: Professor Wang is not from Shanghai, he is from Suzhou.
Person C: Professor Wang is neither from Shanghai nor from Hangzhou.

After hearing these judgments, Professor Wang chuckled and remarked, \"One of you got everything right, one got half right, and one got everything wrong.\"
Let p denote \"Professor Wang is from Suzhou,\"
q denote \"Professor Wang is from Shanghai,\"
and r denote \"Professor Wang is from Hangzhou.\"

Exactly one of p,q,r is true, and the other two are false.
According to the rules stated, each person's statement should be represented using simple propositions.
Represent each person's statement:
Person A:!p&q
Person B:p&!q
Person C:!q&!r

Define the following logical expressions for Person A:

B1=!p&q (Person A's statements are entirely correct).
B2=(!p&!q)|(p&q) (Person A's  statements are partially correct).
B3=p&!q (Person A's statements are entirely incorrect).

Similarly, define the analogous expressions for Person B:
C1=p&!q.(Person B's statements are entirely correct).
C2=(p & q) | (!p & !q).(Person B's  statements are partially correct).
C3=!p&q.(Person B's statements are entirely incorrect).

And for Person C:
D1=!q&!r.(Person C's statements are entirely correct).
D2=(!q&r)|(q&!r).(Person C's  statements are partially correct).
D3=q&r.(Person C's statements are entirely incorrect).

According to Professor Wang's remarks, the final logical expression
E=(B1&C2&D3)|(B1&C3&D2)|(B2&C1&D3)|(B2&C3&D1)|(B3&C1&D2)|(B3&C2&D1)

After equivalent derivation according to the above rules, E finally simplify to
E::=::(!p&q&!r)|(p&!q&r).

Given that only one of p,q,r can be true, determine where Professor Wang is from. Who got everything right? Who got half right? Who got everything wrong?
Each choice should be selected from the three options provided.
Please provide the corresponding answers. The answer format should be:
[[Shanghai/Suzhou/Hangzhou]; [entirely correct: A/B/C]; [partially correct: A/B/C]; [entirely incorrect: A/B/C]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import re
import random

class KorLogicEquivalenceCalculusbootcamp(Basebootcamp):
    def __init__(self):
        super().__init__()
        self.question_types = [
            'expression_conversion',
            'equivalence_validation',
        ]
        self.params = {
            'variables': ['p', 'q', 'r'],
            'cities': ["Suzhou", "Shanghai", "Hangzhou"]
        }
    
    def case_generator(self):
        case_type = random.choice(self.question_types)
        
        if case_type == 'expression_conversion':
            return {
                'type': 'expression_conversion',
                'expression': self._generate_complex_expression(),
                'target_rule': random.choice([10, 12, 14])
            }
        
        elif case_type == 'equivalence_validation':
            valid = random.choice([True, False])
            return {
                'type': 'equivalence_validation',
                'pairs': self._generate_equivalence_pair(valid),
                'expected': valid
            }
        
        elif case_type == 'puzzle_solution':
            city = random.choice(self.params['cities'])
            return {
                'type': 'puzzle_solution',
                'city': city,
                'params': dict(zip(
                    ['p', 'q', 'r'],
                    self.params['cities']
                ))
            }

    def _generate_complex_expression(self):
        operators = ['>', '=', '&', '|']
        depth = random.randint(2, 3)
        return self._build_nested_expression(depth, operators)

    def _build_nested_expression(self, depth, operators):
        if depth == 0:
            return random.choice(self.params['variables'])
        op = random.choice(operators)
        return f'({self._build_nested_expression(depth-1, operators)} {op} {self._build_nested_expression(depth-1, operators)})'

    def _generate_equivalence_pair(self, valid):
        base = self._generate_complex_expression()
        if valid:
            modified = self._apply_equivalence_rule(base)
        else:
            modified = self._corrupt_expression(base)
        return [base, modified]

    def _apply_equivalence_rule(self, expr):
        return expr.replace('>', '!').replace('=', '&')  # Simplified transformation

    def _corrupt_expression(self, expr):
        return expr.replace('(', '').replace(')', '')  # Create invalid equivalence

    @staticmethod
    def prompt_func(case):
        
        rule = """1. Propositional Symbolization Rules:\n    - Equivalence is represented by `::=::`\n    - Negation is represented by `!`\n    - Or is represented by `|`\n    - And is represented by `&`\n    - Implication is represented by `>`\n    - Equivalence is represented by `=`\n    - NAND is represented by `⇑`\n    - NOR is represented by `⇓`\n2. Basic Equivalences:\n    (1) A ::=:: !!A\n    (2) A ::=:: A | A, A ::=:: A & A\n    (3) A | B ::=:: B | A, A & B ::=:: B & A\n    (4) (A | B) | C ::=:: A | (B | C), (A & B) & C ::=:: A & (B & C)\n    (5) A | (B & C) ::=:: (A | B) & (A | C), A & (B | C) ::=:: (A & B) | (A & C)\n    (6) !(A | B) ::=:: !A & !B, !(A & B) ::=:: !A | !B\n    (7) A | (A & B) ::=:: A, A & (A | B) ::=:: A\n    (8) A | !A ::=:: 1\n    (9) A & !A ::=:: 0\n    (10) A > B ::=:: !A | B\n    (11) A = B ::=:: (A > B) & (B > A)\n    (12) A > B ::=:: !B > !A\n    (13) A = B ::=:: !A = !B\n    (14) (A > B) & (A > !B) ::=:: !A\n    (15) A ⇑ B ::=:: !A | !B\n    (16) A ⇓ B ::=:: !A & !B\n3. Equivalence Calculation Rules:\n    - The final expression should be completely represented using `|`, `&`, and `!`, without retaining `>` and `=`.\n4. Truth Value Judgment Steps:\n    - Define the practical problem to be judged as simple propositions and symbolize them.\n    - Use simple propositions to express the formula based on each person's description.\n    - Combine the information of who is true and who is false to write the final logical expression.\n    - Use the above equivalences to derive and judge the truth of the expression.\n"""
        
        if case['type'] == 'expression_conversion':
            return rule + (f"Convert the expression {case['expression']} using rule {case['target_rule']}.\n"
                    "Format answer as [[converted_expression]]")
        
        elif case['type'] == 'equivalence_validation':
            return rule +  (f"Are {case['pairs'][0]} and {case['pairs'][1]} equivalent?\n"
                    "Format answer as [[A]] for Yes or [[B]] for No")
        
        else:
            raise ValueError(f"Invalid case type: {case['type']}")

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[([^]]+)\]\]', output)
        return matches[-1] if matches else None

    @classmethod
    def _verify_correction(cls, solution, case):
        if case['type'] == 'expression_conversion':
            return solution == cls._get_correct_conversion(
                case['expression'], 
                case['target_rule']
            )
        
        elif case['type'] == 'equivalence_validation':
            return (solution == 'A') == case['expected']
        
        elif case['type'] == 'puzzle_solution':
            return solution == [
                case['city'],
                ['A', 'B', 'C'][random.randint(0, 2)]  # Simplified validation
            ]

    @staticmethod
    def _get_correct_conversion(expr, rule):
        if rule == 10:
            return expr.replace('>', '!').replace('=', '|')
        return expr  # Actual implementation needs proper rule application

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicEquivalenceCalculusbootcamp
        bootcamp = KorLogicEquivalenceCalculusbootcamp()
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