"""### 谜题描述
Direct Propositions:
Reflect propositions that assert whether something does or does not possess a certain property, also known as property propositions or subject-predicate propositions.

Examples:
- [1] All metals are conductive.
- [2] Some products of labor are not commodities.

Composition of Direct Propositions:
- Subject (S): The term in the proposition that denotes the object being discussed. Examples include \"metals\" in [1] and \"products of labor\" in [2].
- Predicate (P): The term in the proposition that denotes the property of the object. Examples include \"conductive\" in [1] and \"commodities\" in [2].
- Connectives(C): Words that connect the subject and predicate.
    - Affirmative connective (e.g., \"are\"): Asserts that the subject possesses the property.
    - Negative connective (e.g., \"are not\"): Asserts that the subject does not possess the property.
- Quantifiers(Q): Words that indicate the quantity of objects referred to by the subject.
    - Universal quantifier (e.g., \"all\"): Indicates all members.
    - Particular quantifier (e.g., \"some\"): Indicates at least one member.

Logical Forms of Direct Propositions:
- Universal Affirmative (A): All S are P, abbreviated as SAP.
- Universal Negative (E): No S are P, abbreviated as SEP.
- Particular Affirmative (I): Some S are P, abbreviated as SIP.
- Particular Negative (O): Some S are not P, abbreviated as SOP.
- Singular Affirmative: a is P.
- Singular Negative: a is not P.

Relationships: 
The relationships between declarative propositions are based on the premise that the subject and predicate are identical. 
This identity is referred to as having the same subject (S) and predicate (P). 
There are four types of relationships as follows:
- * Relation:
    - Between A propositions and O propositions, E propositions and I propositions.
    - If one is true, the other is false; if one is false, the other is true.
- # Relation:
    - Between A propositions and E propositions.
    - If one is true, the other is false; if one is false, the other may be true or false.
- & Relation:
    - Between I propositions and O propositions.
    - If one is false, the other is true; if one is true, the other may be false or true.
- % Relation:
    - Between A propositions and I propositions, E propositions and O propositions.
    - If the universal proposition is true, the particular proposition is true; if the particular proposition is false, the universal proposition is false.Example questions are as follows:

<example 0>
All mammals are warm-blooded animals.

1. S is what?
2. P is what?
3. C is what?
4. Q is what?

A.all  B. mammals  C.are  D.warm-blooded animals  

Please answer in the format of [[A/B/C/D];[A/B/C/D];[A/B/C/D];[A/B/C/D]].
</example 0>

<example 1>
Some students do not like mathematics.

1. S is what?
2. P is what?
3. C is what?
4. Q is what?

A. students  B.like mathematics  C.some   D.do not 

Please answer in the format of [[A/B/C/D];[A/B/C/D];[A/B/C/D];[A/B/C/D]].
</example 1>

<example 2>
[1] All products are qualified.
[2] All products are not qualified.
[3] All products are not unqualified.
[4] Some products are unqualified.

Only when S and P are completely identical do they have a relationship. 
Do [1] and [2] have a relationship? 
Do [1] and [3] have a relationship? 
Do [3] and [4] have a relationship?

A. Yes B. No

Please answer in the format of [[A/B];[A/B];[A/B]].
</example 2>

<example 3>
[1] All products are qualified.
[2] All products are unqualified.
[3] No products are unqualified.
[4] Some products are unqualified.

What is the relationship between [1] and [2]? 

What is the relationship between [3] and [4]? 

Choose from the following four types:
A. *  B. #  C. &  D. %

Please answer in the format of [[A/B/C/D];[A/B/C/D]].
</example 3>

<example 4>
What type of proposition is the following statement?
\"Some stars are planets.\"

Please answer in the format of [[SAP/SEP/SIP/SOP]].
</example 4>

<example 5>
What type of proposition is the following statement?
\"All pencils are not pens.\"

Please answer in the format of [[SAP/SEP/SIP/SOP]].
</example 5>

<example 6>
If the proposition SAP is true, then the proposition SOP is what?
If the proposition SIP is true, then the proposition SEP is what?
If the proposition SIP is false, then the proposition SEP is what?
If the proposition SOP is false, then the proposition SAP is what?

Please answer in the format of [[true/false];[true/false];[true/false];[true/false]].
</example 6>

<example 7>
If the proposition SIP is false, then the proposition SOP is what?
If the proposition SOP is false, then the proposition SIP is what?
If the proposition SAP is true, then the proposition SEP is what?
If the proposition SEP is true, then the proposition SAP is what?

Please answer in the format of [[true/false];[true/false];[true/false];[true/false]].
</example 7>

<example 8>
In Class A, with a total of 40 students, they discussed the situation regarding computer typing. Three students, A, B, and C, each expressed their opinions:

- Student A said: \"Li Cong from Class A has not learned how to type on a computer.\"
- Student B said: \"Some students in Class A have learned how to type on a computer.\"
- Student C said: \"Some students in Class A have not learned how to type on a computer.\"

What is the relationship between the statements made by Students B and C among the four types?

Please answer in the format of [[*/#/&/%]].
</example 8>

<example 9>
After a certain tax inspection, four tax inspectors came to the following conclusions:

- Inspector A: All individual businesses did not pay taxes.
- Inspector B: The individual business owner, Mr. Chen, did not pay taxes.
- Inspector C: Some individual businesses have paid taxes.
- Inspector D: Some individual businesses have not paid taxes.

What is the relationship between what Inspector A and Inspector C said among the four types?

Please answer in the format of [[*/#/&/%]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import json
import random
from bootcamp import Basebootcamp

class KorLogicPropositionalLogicConceptsbootcamp(Basebootcamp):
    def __init__(self, s_list=None, p_list=None, problem_types=None, **params):
        super().__init__(**params)
        self.s_list = s_list or ["metals", "products", "students", "mammals", "pencils", "stars", "individual businesses"]
        self.p_list = p_list or ["conductive", "qualified", "like mathematics", "warm-blooded animals", 
                                "pens", "planets", "paid taxes"]
        self.problem_types = problem_types or ["components", "proposition_type", "relationship_exists", 
                                              "relationship_type", "truth_value"]

    def case_generator(self):
        problem_type = random.choice(self.problem_types)
        if problem_type == "components":
            return self._generate_components_case()
        elif problem_type == "proposition_type":
            return self._generate_proposition_type_case()
        elif problem_type == "relationship_exists":
            return self._generate_relationship_exists_case()
        elif problem_type == "relationship_type":
            return self._generate_relationship_type_case()
        elif problem_type == "truth_value":
            return self._generate_truth_value_case()
        else:
            return self._generate_components_case()

    @staticmethod
    def prompt_func(question_case) -> str:
        pt = question_case["problem_type"]
        if pt == "components":
            return KorLogicPropositionalLogicConceptsbootcamp._components_prompt(question_case)
        elif pt == "proposition_type":
            return KorLogicPropositionalLogicConceptsbootcamp._proposition_type_prompt(question_case)
        elif pt == "relationship_exists":
            return KorLogicPropositionalLogicConceptsbootcamp._relationship_exists_prompt(question_case)
        elif pt == "relationship_type":
            return KorLogicPropositionalLogicConceptsbootcamp._relationship_type_prompt(question_case)
        elif pt == "truth_value":
            return KorLogicPropositionalLogicConceptsbootcamp._truth_value_prompt(question_case)
        else:
            return "Unknown problem type"

    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[([^]]+)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return [item.strip() for item in last_match.split(';')]

    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        pt = identity["problem_type"]
        if pt == "components":
            return solution == identity["correct_answer"]
        elif pt == "proposition_type":
            return solution == [identity["correct_type"]]
        elif pt == "relationship_exists":
            return solution == identity["correct_answers"]
        elif pt == "relationship_type":
            return solution == identity["correct_relations"]
        elif pt == "truth_value":
            return solution == identity["correct_values"]
        return False

    # region Case Generators
    def _generate_components_case(self):
        s = random.choice(self.s_list)
        p = random.choice([x for x in self.p_list if x != s])
        prop_type = random.choice(["A", "E", "I", "O"])
        
        if prop_type == "E" and random.random() < 0.5:
            q, c = "all", "are not"
        else:
            qc_map = {
                "A": ("all", "are"), 
                "E": ("no", "are"), 
                "I": ("some", "are"), 
                "O": ("some", "are not")
            }
            q, c = qc_map[prop_type]
        
        proposition = f"{q} {s} {c} {p}." if prop_type != "E" or q == "no" else f"{q} {s} {c} {p}."
        elements = [q, s, c, p]
        random.shuffle(elements)
        
        correct = []
        for key in [s, p, c, q]:
            correct.append(chr(65 + elements.index(key)))
        
        return {
            "problem_type": "components",
            "proposition": proposition,
            "shuffled_elements": elements,
            "correct_answer": correct
        }

    def _generate_proposition_type_case(self):
        s = random.choice(self.s_list)
        p = random.choice([x for x in self.p_list if x != s])
        prop_type = random.choice(["A", "E", "I", "O"])
        
        qc_map = {
            "A": ("all", "are"), 
            "E": ("no", "are"), 
            "I": ("some", "are"), 
            "O": ("some", "are not")
        }
        q, c = qc_map[prop_type]
        
        if prop_type == "E" and random.random() < 0.5:
            q, c = "all", "are not"
        
        proposition = f"{q} {s} {c} {p}." if prop_type != "E" or q == "no" else f"{q} {s} {c} {p}."
        type_map = {
            "A": "SAP", 
            "E": "SEP", 
            "I": "SIP", 
            "O": "SOP"
        }
        return {
            "problem_type": "proposition_type",
            "proposition": proposition,
            "correct_type": type_map[prop_type]
        }

    def _generate_relationship_exists_case(self):
        s = random.choice(self.s_list)
        p = random.choice([x for x in self.p_list if x != s])
        
        prop1 = self._generate_proposition(s, p)
        prop2 = self._generate_proposition(s, p)
        prop3 = self._generate_proposition(
            random.choice(self.s_list), 
            random.choice(self.p_list)
        )
        
        return {
            "problem_type": "relationship_exists",
            "propositions": [
                prop1["proposition"], 
                prop2["proposition"], 
                prop3["proposition"]
            ],
            "correct_answers": ["A", "A", "B"]
        }

    def _generate_relationship_type_case(self):
        s = random.choice(self.s_list)
        p = random.choice(self.p_list)
        
        prop1 = self._generate_proposition(s, p)
        prop2 = self._generate_proposition(s, p)
        
        rel_map = {
            ("A", "O"): "*", 
            ("E", "I"): "*",
            ("A", "E"): "#", 
            ("I", "O"): "&",
            ("A", "I"): "%", 
            ("E", "O"): "%"
        }
        
        type1 = prop1["type"]
        type2 = prop2["type"]
        key = tuple(sorted([type1, type2]))
        correct = rel_map.get(key, "B")
        
        return {
            "problem_type": "relationship_type",
            "propositions": [
                prop1["proposition"], 
                prop2["proposition"]
            ],
            "correct_relations": [correct]
        }

    def _generate_truth_value_case(self):
        base_prop = self._generate_proposition_type_case()
        base_type = base_prop["correct_type"]
        
        relations = {
            "SAP": [("SOP", "false")],
            "SEP": [("SIP", "false")],
            "SIP": [("SOP", None)],
            "SOP": [("SIP", None)]
        }
        
        questions = []
        correct = []
        for _ in range(4):
            related_type = random.choice(["SAP", "SEP", "SIP", "SOP"])
            questions.append(f"If {base_type} is true, then {related_type} is ___?")
            if (base_type, related_type) in [("SAP", "SOP"), ("SEP", "SIP")]:
                correct.append("false")
            else:
                correct.append(random.choice(["true", "false"]))
        
        return {
            "problem_type": "truth_value",
            "base_proposition": base_prop["proposition"],
            "questions": questions,
            "correct_values": correct
        }

    def _generate_proposition(self, s, p):
        prop_type = random.choice(["A", "E", "I", "O"])
        qc_map = {
            "A": ("all", "are"), 
            "E": ("no", "are"), 
            "I": ("some", "are"), 
            "O": ("some", "are not")
        }
        q, c = qc_map[prop_type]
        return {
            "proposition": f"{q} {s} {c} {p}.",
            "type": prop_type,
            "S": s,
            "P": p
        }
    # endregion

    # region Prompt Templates
    @staticmethod
    def _components_prompt(case):
        options = "\n".join([
            f"{chr(65+i)}. {case['shuffled_elements'][i]}" 
            for i in range(4)
        ])
        return (
            f"Analyze the components of this proposition:\n"
            f"{case['proposition']}\n\n"
            "1. Subject (S)\n2. Predicate (P)\n"
            "3. Connective (C)\n4. Quantifier (Q)\n"
            f"Options:\n{options}\n"
            "Answer format: [[A/B/C/D;A/B/C/D;A/B/C/D;A/B/C/D]]"
        )

    @staticmethod
    def _proposition_type_prompt(case):
        return (
            f"Classify this proposition:\n"
            f"{case['proposition']}\n"
            "Choose from: [[SAP/SEP/SIP/SOP]]"
        )

    @staticmethod
    def _relationship_exists_prompt(case):
        props = "\n".join([
            f"[{i+1}] {p}" 
            for i, p in enumerate(case['propositions'])
        ])
        return (
            "Determine if these propositions share S and P:\n"
            f"{props}\n"
            "Answer format: [[A/B;A/B;A/B]] (Yes/No)"
        )

    @staticmethod
    def _relationship_type_prompt(case):
        return (
            "Determine the logical relationship:\n"
            f"1. {case['propositions'][0]}\n"
            f"2. {case['propositions'][1]}\n"
            "Choose from: [[*/#/&/%]]"
        )

    @staticmethod
    def _truth_value_prompt(case):
        questions = "\n".join([
            f"Q{i+1}: {q}" 
            for i, q in enumerate(case['questions'])
        ])
        return (
            f"Given: {case['base_proposition']}\n"
            f"Answer these:\n{questions}\n"
            "Format: [[true/false;...]]"
        )
    # endregion
