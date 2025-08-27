"""### 谜题描述
Symbols: Use # for necessity, $ for possibility, letters like p, q, r... for propositions, ! for negation, + for conjunction, - for disjunction, = for equivalence, and > for implication.

1. Four Modal Proposition Relationships:
(1) * Relationship:
- Pairs of Propositions: #p and $¬p; #¬p and $p
- Property: They cannot both be true or both be false.

(2) x Relationship:
- Pairs of Propositions: #p and #¬p
- Property: They cannot both be true, but they can both be false.

(3) @ Relationship:
- Pairs of Propositions: $p and $¬p
- Property: They cannot both be false, but they can both be true.

(4) % Relationship:
- Pairs of Propositions: #p and $p; #¬p and $¬p
- Property: They can both be true or both be false.

2. Modal Logic Inference Formulas:
(1) #p ←→ !$!p
(2) $p ←→ !#!p
(3) #!p ←→ !$p
(4) $!p ←→ !#p
(5) #p → !#!p
(6) #!p → !#p
(7) !$p → $!p
(8) !$!p → $p
(9) #p → $p
(10) #!p → $!p
(11) !$p → !#p
(12) !$!p → !#!p
(13) #p → p
(14) #!p → !p
(15) p → $p
(16) !p → $!pExample questions are as follows:

<example 0>
Symbolise the following modal propositions:
\"Science cannot be a one-man endeavour.\"

Use p to denote \"Science is a human endeavour.\"
Please give your answer in [[]] format.
</example 0>

<example 1>
Symbolise the following modal propositions:

(1) There must be either life or no life in a fire. Use p to denote \"there is life on Mars\".
(2) If Li Ming plays well, then it is possible for him to win the championship. Use p to indicate that \"Li Ming plays well\" and q to indicate that \"he wins the championship\".

First symbolize the propositions, then enclose them in parentheses, and finally add modal symbols around them.
Please give your answer in [[];[]] format.
</example 1>

<example 2>
What is the relationship between each of the following sentences?
(1) \"The Chinese women's volleyball team is definitely victorious\" and \"The Chinese women's volleyball team may not win.\"
(2) \"This project will definitely be completed ahead of schedule\" and \"This project will definitely not be completed ahead of schedule.\"

And the options for the relationships are:

A. * relationship
B. x relationship
C. @ relationship
D. % relationship

Please answer in the format of [[A/B/C/D];[A/B/C/D]].
</example 2>

<example 3>
What is the relationship between each of the following sentences?
(1) \"The task of developing an anti-SARS vaccine may be completed this year\" and \"The task of developing an anti-SARS vaccine may not be completed this year.\"
(2) \"The Brazil football team will definitely win the championship\" and \"The Brazil football team may win the championship.\"

And the options for the relationships are:

A. * relationship
B. @ relationship
C. % relationship
D. x relationship

Please answer in the format of [[A/B/C/D];[A/B/C/D]].
</example 3>

<example 4>
\"Arrogance necessarily results in falling behind\" 
can infer \"Arrogance cannot possibly not result in falling behind.\"
 Which truth-value modal reasoning formula corresponds to this?

Please answer in the format of [[number]].
</example 4>

<example 5>
\"A person cannot necessarily pull their own hair and leave the earth\" 
can infer \"A person cannot possibly pull their own hair and leave the earth\". 
Which truth-value modal reasoning formula corresponds to this?

Please answer in the format of [[number]].
</example 5>

<example 6>
\"The experiment is not necessarily not going to succeed\"
can infer \"The experiment may possibly succeed”. 
Which truth-value modal reasoning formula corresponds to this?

Please answer in the format of [[number]].
</example 6>

<example 7>
According to the truth modal reasoning formula 9, what can be inferred from \"Xiao Lin will necessarily win the championship\"?

A. Xiao Lin will possibly win the championship.
B. Xiao Lin will certainly win the championship.
C. Xiao Lin cannot win the championship.
D. Xiao Lin will never win the championship.

Please answer in the format of [[A/B/C/D]].
</example 7>

<example 8>
Based on the truth modal reasoning formula 15, what can be inferred from \"There is necessarily a connection between things\"?

A. There is no connection between things.
B. There might be a connection between things.
C. There is a connection between things.
D. It is impossible for things to be connected.

Please answer in the format of [[A/B/C/D]].
</example 8>

<example 9>
Based on the truth modal reasoning formula 16, what can be inferred from \"Team A did not win the championship\"?

A. Team A  won the championship.
B. Team A will not win the championship.
C. Team A cannot win the championship.
D. Team A might not have won the championship.

Please answer in the format of [[A/B/C/D]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from bootcamp import Basebootcamp

class KorLogicTruthValueModalPropositionsbootcamp(Basebootcamp):
    def __init__(self, **params):
        super().__init__(**params)
        self.problem_types = params.get('problem_types', {
            'relationship': 0.4,
            'symbolization': 0.3,
            'formula': 0.2,
            'multiple_choice_formula': 0.1
        })
        self.propositions = params.get('propositions', {
            'p': [
                "the Chinese women's volleyball team is victorious",
                "the project is completed ahead of schedule",
                "there is life on Mars",
                "the experiment succeeds",
                "the Brazil football team wins the championship",
                "Science is a human endeavour",
                "Xiao Lin wins the championship",
                "Team A wins the championship",
                "the connection between things exists",
                "the task of developing an anti-SARS vaccine is completed this year",
            ],
            'q': [
                "Li Ming plays well",
                "he wins the championship",
                "there is no life in a fire",
                "arrogance results in falling behind",
                "the experiment is going to succeed",
            ]
        })
        self.formulas = [
            {'number': 1, 'premise': '#p', 'conclusion': '!$!p'},
            {'number': 5, 'premise': '#p', 'conclusion': '!#!p'},
            {'number': 9, 'premise': '#p', 'conclusion': '$p'},
            {'number': 15, 'premise': 'p', 'conclusion': '$p'},
            {'number': 16, 'premise': '!p', 'conclusion': '$!p'},
        ]

    def case_generator(self):
        problem_type = random.choices(
            list(self.problem_types.keys()),
            weights=list(self.problem_types.values()),
            k=1
        )[0]
        
        if problem_type == 'relationship':
            return self._generate_relationship_case()
        elif problem_type == 'symbolization':
            return self._generate_symbolization_case()
        elif problem_type == 'formula':
            return self._generate_formula_case()
        elif problem_type == 'multiple_choice_formula':
            return self._generate_mc_formula_case()
        else:
            return {}

    def _generate_relationship_case(self):
        relations = [
            {'type': 'A', 'pairs': [('#', False, 'p'), ('$', True, 'p')]},
            {'type': 'A', 'pairs': [('#', True, 'p'), ('$', False, 'p')]},
            {'type': 'B', 'pairs': [('#', False, 'p'), ('#', True, 'p')]},
            {'type': 'C', 'pairs': [('$', False, 'p'), ('$', True, 'p')]},
            {'type': 'D', 'pairs': [('#', False, 'p'), ('$', False, 'p')]},
            {'type': 'D', 'pairs': [('#', True, 'p'), ('$', True, 'p')]},
        ]
        selected = random.choice(relations)
        p = random.choice(self.propositions['p'])
        
        statements = []
        for modality, negated, _ in selected['pairs']:
            statements.append(self._modal_to_sentence(modality, negated, p))
        
        return {
            'type': 'relationship',
            'statements': statements,
            'correct_answer': selected['type']
        }

    def _generate_symbolization_case(self):
        prop = random.choice(['p', 'q'])
        sentence = random.choice(self.propositions[prop])
        has_modal = random.random() < 0.5
        has_negation = random.random() < 0.5
        
        components = []
        if has_modal:
            modality = random.choice(['#', '$'])
            components.append(modality)
        if has_negation:
            components.append('!')
        components.append(prop)
        
        return {
            'type': 'symbolization',
            'sentence': self._construct_sentence(has_modal, has_negation, sentence),
            'symbol_defs': {prop: sentence},
            'correct_answer': ''.join(components)
        }

    def _generate_formula_case(self):
        formula = random.choice(self.formulas)
        p = random.choice(self.propositions['p'])
        
        premise = self._parse_expression(formula['premise'], p)
        conclusion = self._parse_expression(formula['conclusion'], p)
        
        return {
            'type': 'formula',
            'premise': premise,
            'conclusion': conclusion,
            'correct_answer': formula['number']
        }

    def _generate_mc_formula_case(self):
        formula = random.choice([f for f in self.formulas if f['number'] in [9,15,16]])
        p = random.choice(self.propositions['p'])
        
        premise = self._parse_expression(formula['premise'], p)
        options = self._generate_options(formula, p)
        
        return {
            'type': 'multiple_choice_formula',
            'formula_number': formula['number'],
            'premise': premise,
            'options': options,
            'correct_answer': self._get_correct_option(formula, options)
        }

    @staticmethod
    def prompt_func(question_case):
        if question_case['type'] == 'relationship':
            return f'''What is the relationship between these propositions?
(1) "{question_case['statements'][0]}"
(2) "{question_case['statements'][1]}"

Options:
A. * relationship
B. x relationship
C. @ relationship
D. % relationship

Answer in [[A/B/C/D]]'''
        
        elif question_case['type'] == 'symbolization':
            symbols = ", ".join([f"'{k}' means '{v}'" for k,v in question_case['symbol_defs'].items()])
            return f'''Symbolize: "{question_case['sentence']}"

Using: {symbols}
Format your answer using modal symbols (#,$,!) and proposition letters. Put your answer in [[...]]'''
        
        elif question_case['type'] == 'formula':
            return f'''Which formula corresponds to this inference?
Premise: {question_case['premise']}
Conclusion: {question_case['conclusion']}

Answer with formula number in [[number]]'''
        
        elif question_case['type'] == 'multiple_choice_formula':
            options = "\n".join([f"{k}: {v}" for k,v in question_case['options'].items()])
            return f'''According to formula {question_case['formula_number']}, what can be inferred from:
"{question_case['premise']}"?

Options:
{options}

Answer in [[A/B/C/D]]'''
        
        return "Invalid question type"

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        case_type = identity.get('type')
        correct = identity.get('correct_answer')
        
        if case_type == 'relationship':
            return solution.upper() == correct.upper()
        
        elif case_type == 'symbolization':
            return solution.replace(' ', '') == correct.replace(' ', '')
        
        elif case_type == 'formula':
            return str(solution) == str(correct)
        
        elif case_type == 'multiple_choice_formula':
            return solution.upper() == correct.upper()
        
        return False

    # Helper methods
    def _modal_to_sentence(self, modality, negated, prop):
        prop = prop[0].upper() + prop[1:]
        if modality == '#':
            if negated:
                return f"It is definitely not the case that {prop}."
            return f"It is definitely true that {prop}."
        elif modality == '$':
            if negated:
                return f"It is possibly not the case that {prop}."
            return f"It is possibly true that {prop}."
        else:
            if negated:
                return f"It is not the case that {prop}."
            return f"{prop}."

    def _construct_sentence(self, has_modal, has_negation, prop):
        prop = prop[0].upper() + prop[1:]
        parts = []
        if has_modal:
            parts.append("It is necessarily true that" if random.random() < 0.5 else "It must be that")
        if has_negation:
            parts.append("not")
        parts.append(prop)
        return ' '.join(parts) + '.'

    def _parse_expression(self, expr, prop):
        modality, negated, _ = self._parse_symbolic(expr)
        return self._modal_to_sentence(modality, negated, prop)

    def _parse_symbolic(self, expr):
        modality = None
        negated = False
        rest = expr
        
        while rest.startswith('!'):
            negated = not negated
            rest = rest[1:]
        
        if rest.startswith(('#', '$')):
            modality = rest[0]
            rest = rest[1:]
        
        while rest.startswith('!'):
            negated = not negated
            rest = rest[1:]
        
        return modality, negated, rest

    def _generate_options(self, formula, prop):
        if formula['number'] == 9:
            return {
                'A': f"It is possibly true that {prop}",
                'B': f"It is necessarily true that {prop}",
                'C': f"It is not true that {prop}",
                'D': f"It is impossible that {prop}"
            }
        elif formula['number'] == 15:
            return {
                'A': "There is no connection between things",
                'B': "There might be a connection between things",
                'C': "There is a connection between things",
                'D': "It is impossible for things to be connected"
            }
        elif formula['number'] == 16:
            return {
                'A': "Team A won the championship",
                'B': "Team A will not win the championship",
                'C': "Team A cannot win the championship",
                'D': "Team A might not have won the championship"
            }
        return {}

    def _get_correct_option(self, formula, options):
        if formula['number'] == 9:
            return 'A'
        elif formula['number'] == 15:
            return 'C' if formula['premise'] == 'p' else 'B'
        elif formula['number'] == 16:
            return 'D'
        return ''
