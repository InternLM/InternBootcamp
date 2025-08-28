"""### 谜题描述
Universal Quantifier: Use Ax to denote \"for all x\".
Existential Quantifier: Use Ex to denote \"there exists some x\".

Logical Connectives:
Conjunction: Use &
Disjunction: Use |
Implication: Use ⇒
Negation: Use ∼

In general, a predicate P with n (n > 1) individual variables is called an n-ary predicate, denoted as P(x1, x2, ..., xn). When n = 1, P(x) denotes the property P; when n ≥ 2, P(x1, x2, ..., xn) denotes the relationship P among x1, x2, ..., xn.

Predicates without individual variables are called 0-ary predicates. For example, F(a), G(a, b), P(a1, ..., an) are all 0-ary predicates.

Let D be the domain of individuals.
\"All x in D have property F\" is symbolized as AxF(x).
\"Some x in D have property F\" is symbolized as ExF(x).
\"For all x in D, if x has property F, then x has property G\" is symbolized as Ax(F(x) ⇒ G(x)).
\"Some x in D have both properties F and G\" is symbolized as Ex(F(x) & G(x)).
\"For all x, y in D, if x has property F and y has property G, then x and y have relationship H\" is symbolized as AxAy(F(x) & F(y) ⇒ H(x, y)).
\"For all x in D, if x has property F, then there exists some y with property G such that x and y have relationship H\" is symbolized as Ax(F(x) ⇒ Ey(G(y) & H(x, y))).
\"There exists some x in D with property F, and for all y in D, if y has property G, then x and y have relationship H\" is symbolized as Ex(F(x) & Ay(G(y) ⇒ H(x, y))).Example questions are as follows:

<example 0>
In first-order logic, symbolize the following propositions using 0-ary predicates:
(1) Only 2 is a prime number, 4 is a composite number.
(2) If 5 is greater than 4, then 4 is greater than 6.

For (1), define a unary predicate F(x): x is a prime number. 
The proposition can be symbolized as?

For (2), define a binary predicate G(x, y): x > y. 
The proposition can be symbolized as?

Please provide the answers in the format [[];[]].
</example 0>

<example 1>
In individual domains limited to (a) and (b) conditions, symbolize the following two propositions:
(1) All humans breathe.
(2) Some people write with their left hand.
Where:
(a) Individual domain D1 is the set of humans.
(b) Individual domain D2 is the universal domain.

(a) 
Let F(x): x breathes.
G(x): x writes with their left hand.
In D1, apart from humans, there is nothing else,
thus (1) symbolizes as? (2) symbolizes as?

(b) 
In D2, besides humans, there are all things, 
so when symbolizing, humans must be separated first. 
Introduce predicate M(x): x is a human. 
In D2, clarify (1) and (2) as follows:
(1) For all individuals in the universe, if the individual is human, then they breathe.
(2) There exists an individual in the universe who writes with their left hand (or more precisely, there exists such an individual who is human and writes with their left hand).

Therefore, (1) symbolizes as?(2) symbolizes as?

Please provide the answers in the format [[];[];[];[]].
</example 1>

<example 2>
Symbolize the following propositions:
(1) All humans have black hair.
(2) Some people have been to the moon.
(3) No one has been to Jupiter.
(4) Students studying in the United States are not necessarily Asian.

Using the universal domain.
Let M(x): x is a human,
(1) Let F(x): x has black hair. Proposition (1) symbolizes as?
(2) Let G(x): x has been to the moon. Proposition (2) symbolizes as?
(3) Let H(x): x has been to Jupiter. Proposition (3) symbolizes as?
(4) Let F(x): x studies in the United States, G(x): x is Asian. Proposition (4) symbolizes as?

Please provide the answers in the format [[];[];[];[]].
</example 2>

<example 3>
Using the universal domain, symbolize the proposition:
Some rabbits run faster than all turtles.

Let F(x): x is a rabbit,
G(y): y is a turtle,
H(x,y): x runs faster than y,
L(x,y): x runs equally fast as y.

Thus, this proposition can be symbolized as?

Please provide the answer in the format [[]].
</example 3>

<example 4>
Given the domain of individuals as the set of natural numbers(N),
F(x): x is even,
G(x): x is prime,

Using 0-ary predicates, symbolize the following propositions:
(1) 2 is an even prime number.
(2) If 2 is prime, then 4 is not prime.
(3) Only 2 is prime, for 6 to be prime.
(4) Unless 6 is prime, 4 is prime.

Please provide the answers in the format [[];[];[];[]].
</example 4>

<example 5>
Let the domain of individuals be D = {0, 1, 2, ..., 10}. 
Symbolize the following propositions:

(1) All even numbers in D are divisible by 2.
(2) Some even numbers in D are multiples of 4.

For (1), using predicates:
G(x): x is even,
H(x): x is divisible by 2,
(1) can be symbolized as?

For (2), using predicates:
G(x): x is even,
R(x): x is a multiple of 4,
(2) can be symbolized as?

Please provide the answers in the format [[];[]].
</example 5>

<example 6>
Let the domain of individuals be D = {x |x is a person}.
Symbolize the following propositions:

(1) All Chinese people use chopsticks to eat.
(2) Some Americans do not live in the United States.

For (1), using predicates:
F(x): x is Chinese,
G(x): x uses chopsticks to eat,
(1) can be symbolized as?

For (2), using predicates:
F(x): x is American,
G(x): x lives in the United States,
(2) can be symbolized as?

Please provide the answers in the format [[];[]].
</example 6>

<example 7>
Using the universal domain of individuals, symbolize the following propositions:

(1) Any even number x and y have a common divisor greater than 1.
(2) There exist odd numbers x and y that do not have a common divisor greater than 1.
(3) It is true that some trains are faster than all cars.

For (1), using predicates:
F(x): x is even,
H(x,y): x and y have a common divisor greater than 1,
(1) can be symbolized as?

For (2), using predicates:
G(x): x is odd,
H(x,y): x and y have a common divisor greater than 1,
(2) can be symbolized as?

For (3), using predicates:
F(x): x is a train,
G(y): y is a car,
H(x,y): x is faster than y,
(3) can be symbolized as?

Please provide the answers in the format [[];[];[]].
</example 7>

<example 8>
Using the domain of individuals as the set of integers Z, 
symbolize the following statement:
\"For any x and y, there exists a z such that x + y = z.\"
Let H(x, y, z) denote x + y = z. 
How can this be symbolized?

Please provide the answer in the format [[]].
</example 8>

<example 9>
Using the domain of individuals as the set of real numbers R, 
symbolize the following proposition:
\"For every ε > 0, there exists λ > 0 such that whenever |x - x0| < λ, it holds that |f(x) - f(x0)| < ε.\"

Let L(x): x > 0,
M(x, y, z): |x - y| < z,
N(x, y, z): |f(x) - f(y)| < z.

How can this be symbolized?

Please provide the answer in the format [[]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from collections import OrderedDict
from bootcamp import Basebootcamp

class KorLogicPredicateLogicFormalizationbootcamp(Basebootcamp):
    def __init__(self, num_problems=3, max_quantifiers=3):
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

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, flags=re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].replace('\n', ' ').strip()
        return [s.strip() for s in last_match.split(';') if s.strip()]

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if not isinstance(solution, list) or len(solution) != len(identity["problems"]):
                return False
            return all(
                cls._normalize(sol) == cls._normalize(prob["correct_answer"])
                for sol, prob in zip(solution, identity["problems"])
            )
        except Exception:
            return False

    @staticmethod
    def _normalize(expr):
        return expr.replace(' ', '').upper()

    # Enhanced problem generators
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

    # New problem types
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
