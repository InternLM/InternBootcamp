"""### 谜题描述
In a simple conjunctive form (simple disjunctive form) containing n propositional variables, if each propositional variable and its negation appear exactly once, and the propositional variables or their negations are arranged in ascending order of subscripts or in lexicographical order, such a simple conjunctive form (simple disjunctive form) is called a paired conjunctive term (paired disjunctive term).
If the true assignment of a paired conjunctive term corresponds to a binary number equal to hexadecimal number i, this paired conjunctive term is denoted as mi (lowercase m). For example, the true assignment of p∧q is 11, and the binary number is 11, corresponding to hexadecimal number 3, denoted as m3.
If the false assignment of a paired disjunctive term corresponds to a binary number equal to hexadecimal number i, this paired disjunctive term is denoted as Mi (uppercase M). For example, the false assignment of ¬p∨¬q∨¬r is 111, and the binary number is 111, corresponding to hexadecimal number 7, denoted as M7.
The disjunctive normal form (conjunctive normal form) consisting of all paired conjunctive terms (paired disjunctive terms) is called the principal disjunctive normal form (principal conjunctive normal form).
Given a formula A containing n propositional variables:
- If the principal disjunctive normal form of A includes all 2^n paired conjunctive terms, A is a tautology.
- If the principal disjunctive normal form of A includes no paired conjunctive terms, A is a contradiction.
- If the principal disjunctive normal form of A includes m0, A is a basic formula.
- If the indices i of the paired conjunctive terms included in the principal disjunctive normal form of A are all even, A is an all-even formula.
- If the indices i of the paired conjunctive terms included in the principal disjunctive normal form of A are all odd, A is an all-odd formula.Example questions are as follows:

<example 0>
According to the above rules, what are the paired conjunctive terms of (¬p^¬q^r)∨(¬p^q^r)? How can this expression be denoted?
The answer should be in the format [[paired conjunctive terms:...]; [denoted:...]], with multiple paired conjunctive terms separated by commas.
</example 0>

<example 1>
According to the rules above, what are the paired disjunctive terms of (p∨¬q∨r)^(¬p∨¬q∨r)? How can this expression be denoted?
The answer should be in the format [[paired disjunctive terms:...];[denoted:...]], with multiple paired conjunctive terms separated by commas.
</example 1>

<example 2>
Identify ¬p∧¬q∧¬r as: (select all that apply)
A. Tautology B. Contradiction C. Basic formula D. All-even formula E. All-odd formula F. None of the above.
The answer format should be like [[AB...]].
</example 2>

<example 3>
Identify (¬p∧¬q∧r)∨ (p∧q∧r) as: (select all that apply)
A. Tautology B. Contradiction C. Basic formula D. All-even formula E. All-odd formula F. None of the above.
The answer format should be like [[AB...]].
</example 3>

<example 4>
Determine whether (¬p∧¬q∧¬r)V(¬p∧¬q∧r)V(¬p∧q∧r)V(p∧¬q∧r)V(p∧q∧r) conforms to the principal disjunctive normal form or principal conjunctive normal form? If yes, how can it be denoted?
The answer format is as follows: if the statement conforms to the main disjunctive or conjunctive normal form, the answer should be formatted as [[A];[denoted expression]]. If it does not conform, the format should be [[B]].
</example 4>

<example 5>
Determine whether (p∨r)∧(¬q∨r)∧(¬p∨q∨¬r) conforms to the principal disjunctive normal form or principal conjunctive normal form? If yes, how can it be denoted?
The answer format is as follows: if the statement conforms to the main disjunctive or conjunctive normal form, the answer should be formatted as [[A];[denoted expression]]. If it does not conform, the format should be [[B]].
</example 5>

<example 6>
Given that formula A contains 4 propositional variables, what should it be denoted as if it is both a tautology and a basic form? The answer format is [[]].
</example 6>

<example 7>
Given that formula A contains 4 propositional variables, how many formulas satisfy the conditions of being both a basic form and an all-even form?
The answer is a single number, in the format [[]].
</example 7>

<example 8>
A research institute needs to select 1-2 members from 3 key researchers A, B, and C to study abroad. Due to work requirements, the selection must satisfy the following conditions:

1. If A goes, then C must go.
2. If B goes, then C cannot go.
3. If C does not go, then either A or B can go.

Let p: A goes
Let q: B goes
Let r: C goes

Based on the given conditions, the formula can be derived as:
(p → r) ∧ (q → ¬r) ∧ (¬r → (p ∨ q))

The true assignments of this formula are the feasible selection schemes. Through derivation, we get:
(p → r) ∧ (q → ¬r) ∧ (¬r → (p ∨ q)) ↔ (¬p ∧ ¬q ∧ r) ∨ (¬p ∧ q ∧ ¬r) ∨ (p ∧ ¬q ∧ r)

The formula (¬p ∧ ¬q ∧ r) ∨ (¬p ∧ q ∧ ¬r) ∨ (p ∧ ¬q ∧ r) is in principal disjunctive normal form and can be denoted as what? This formula belongs to: (multiple choice)
A. Tautology B. Contradiction C. Basic Form D. All-Even Form E. All-Odd Form F. None of the Above

Answer format: [[denoted expression];[options]]
</example 8>

<example 9>
A research institute needs to select 1-2 members from 3 key researchers A, B, and C to study abroad. Due to work requirements, the selection must satisfy the following conditions:

1. If A goes, then C must go.
2. If B goes, then C cannot go.
3. If C does not go, then either A or B can go.

Let p: A goes
Let q: B goes
Let r: C goes

Based on the given conditions, the formula can be derived as:
(p → r) ∧ (q → ¬r) ∧ (¬r → (p ∨ q))

The true assignments of this formula are the feasible selection schemes. Through derivation, we get:
(p → r) ∧ (q → ¬r) ∧ (¬r → (p ∨ q)) ↔ (¬p ∧ ¬q ∧ r) ∨ (¬p ∧ q ∧ ¬r) ∨ (p ∧ ¬q ∧ r), which can be denoted as m1 ∨ m2 ∨ m5. 
Based on the three true assignments represented, what are the feasible selection schemes? 

Only give the letters of the people selected to go, separated by commas within a scheme, and different schemes separated by []; format: [[];[];..].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import re
import random

class KorLogicDisjunctiveNormalFormAndConjunctiveNormalFormbootcamp(Basebootcamp):
    def __init__(self, max_variables=3, **params):
        super().__init__(**params)
        self.max_variables = max_variables  # p,q,r,s etc.

    def case_generator(self):
        problem_type = random.choice(['classify', 'denote'])
        n = random.randint(2, self.max_variables)
        variables = ['p', 'q', 'r', 's'][:n]
        case = {'variables': variables, 'n': n}

        if problem_type == 'classify':
            # 生成主析取范式案例
            max_terms = 2 ** n
            term_count = random.choice([
                0, max_terms] + [random.randint(1, max_terms-1) for _ in range(3)]
            )
            terms = random.sample(range(max_terms), term_count) if 0 < term_count < max_terms else (
                [] if term_count == 0 else list(range(max_terms)))

            # 确定正确选项
            correct_options = []
            if term_count == max_terms:
                correct_options.append('A')
            elif term_count == 0:
                correct_options.append('B')
            else:
                has_m0 = False
                all_even = True
                all_odd = True
                for i in terms:
                    if i == 0:
                        has_m0 = True
                    if i % 2 != 0:
                        all_even = False
                    if i % 2 == 0:
                        all_odd = False
                if has_m0:
                    correct_options.append('C')
                if all_even and terms:
                    correct_options.append('D')
                if all_odd and terms:
                    correct_options.append('E')
                if not correct_options:
                    correct_options.append('F')

            # 构建表达式
            expr = " ∨ ".join([f"({self._get_conj_term(i, variables)})" for i in terms]) if terms else "∅"

            case.update({
                'type': 'classify',
                'expression': expr,
                'terms': terms,
                'correct_options': correct_options
            })

        elif problem_type == 'denote':
            form_type = random.choice(['disjunctive', 'conjunctive'])
            max_terms = 2 ** n
            
            if form_type == 'disjunctive':
                # 主析取范式
                term_count = random.randint(1, max_terms-1)
                terms = random.sample(range(max_terms), term_count)
                expr = " ∨ ".join([f"({self._get_conj_term(i, variables)})" for i in terms])
                denotation = " ∨ ".join([f"m{i}" for i in sorted(terms)])
            else:
                # 主合取范式
                # 生成假赋值对应的索引
                term_count = random.randint(1, max_terms-1)
                false_assignments = random.sample(range(max_terms), term_count)
                expr_parts = [self._get_disj_term(i, variables) for i in false_assignments]
                expr = " ∧ ".join([f"({part})" for part in expr_parts])
                denotation = " ∧ ".join([f"M{i}" for i in sorted(false_assignments)])
                terms = false_assignments

            case.update({
                'type': 'denote',
                'form_type': form_type,
                'expression': expr,
                'terms': terms,
                'correct_denote': denotation
            })

        return case

    @staticmethod
    def _get_conj_term(i, variables):
        """生成合取式项（主析取范式用）"""
        n = len(variables)
        binary = bin(i)[2:].zfill(n)
        literals = []
        for idx in range(n):
            if binary[idx] == '1':
                literals.append(variables[idx])
            else:
                literals.append(f"¬{variables[idx]}")
        return " ∧ ".join(literals)

    @staticmethod
    def _get_disj_term(i, variables):
        """生成析取式项（主合取范式用）"""
        n = len(variables)
        binary = bin(i)[2:].zfill(n)
        literals = []
        for idx in range(n):
            if binary[idx] == '0':  # 假赋值对应否定
                literals.append(variables[idx])
            else:
                literals.append(f"¬{variables[idx]}")
        return " ∨ ".join(literals)

    @staticmethod
    def prompt_func(question_case):
        
        rule = 'In a simple conjunctive form (simple disjunctive form) containing n propositional variables, if each propositional variable and its negation appear exactly once, and the propositional variables or their negations are arranged in ascending order of subscripts or in lexicographical order, such a simple conjunctive form (simple disjunctive form) is called a paired conjunctive term (paired disjunctive term).\nIf the true assignment of a paired conjunctive term corresponds to a binary number equal to hexadecimal number i, this paired conjunctive term is denoted as mi (lowercase m). For example, the true assignment of p∧q is 11, and the binary number is 11, corresponding to hexadecimal number 3, denoted as m3.\nIf the false assignment of a paired disjunctive term corresponds to a binary number equal to hexadecimal number i, this paired disjunctive term is denoted as Mi (uppercase M). For example, the false assignment of ¬p∨¬q∨¬r is 111, and the binary number is 111, corresponding to hexadecimal number 7, denoted as M7.\nThe disjunctive normal form (conjunctive normal form) consisting of all paired conjunctive terms (paired disjunctive terms) is called the principal disjunctive normal form (principal conjunctive normal form).\nGiven a formula A containing n propositional variables:\n- If the principal disjunctive normal form of A includes all 2^n paired conjunctive terms, A is a tautology.\n- If the principal disjunctive normal form of A includes no paired conjunctive terms, A is a contradiction.\n- If the principal disjunctive normal form of A includes m0, A is a basic formula.\n- If the indices i of the paired conjunctive terms included in the principal disjunctive normal form of A are all even, A is an all-even formula.\n- If the indices i of the paired conjunctive terms included in the principal disjunctive normal form of A are all odd, A is an all-odd formula.\n'
        
        if question_case['type'] == 'classify':
            return rule + (
                f"给定逻辑表达式：\n{question_case['expression']}\n"
                "根据主范式分类规则判断属于哪些类别？\n"
                "A. 永真式 B. 矛盾式 C. 基本式 D. 全偶式 E. 全奇式 F. 以上都不是\n"
                "答案格式：[[大写字母组合]] 例如[[AB]]"
            )
        elif question_case['type'] == 'denote':
            return rule + (
                f"将表达式转换为标准记号形式：\n{question_case['expression']}\n"
                "要求如下：每个配对合取项用 m 或 M 表示。数字直接跟在字母后面，不使用角标（下标）。数字与字母之间不加空格。各项之间用逻辑运算符连接。"
                "答案格式：[[记号表达式]] 例如[[m1∨m3]]或[[M2∧M5]]."
            )

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity['type'] == 'classify':
                sol_set = set(solution.upper())
                truth_set = set(identity['correct_options'])
                return sol_set == truth_set
            
            elif identity['type'] == 'denote':
                # 标准化比较
                sol = re.sub(r'\s+', '', solution).lower().split('∨') if '∨' in solution else re.sub(r'\s+', '', solution).lower().split('∧')
                truth = re.sub(r'\s+', '', identity['correct_denote']).lower().split('∨') if '∨' in identity['correct_denote'] else re.sub(r'\s+', '', identity['correct_denote']).lower().split('∧')
                
                # 检查元素集合是否相同
                return set(sol) == set(truth) and len(sol) == len(truth)
            
            return False
        except:
            return False

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicDisjunctiveNormalFormAndConjunctiveNormalFormbootcamp
        bootcamp = KorLogicDisjunctiveNormalFormAndConjunctiveNormalFormbootcamp()
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
