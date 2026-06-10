import copy
import random
from typing import Any, Dict, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


Entities = [
    # Set1 animals
    'cat', 'dog', 'pig', 'parrot', 'eagle', 'squirrel', 'penguin', 'lion', 'tiger', 'donkey',
    'leopard', 'cheetah', 'grizzly bear', 'polar bear', 'sun bear', 'panda bear', 'black bear',
    'turtle', 'crocodile', 'elephant', 'panther', 'cow', 'rabbit', 'hare', 'buffalo', 'baboon',
    'sheep', 'whale', 'jellyfish', 'carp', 'goldfish', 'viperfish', 'starfish', 'catfish',
    'oscar', 'zander', 'sea bass', 'swordfish', 'salmon', 'halibut', 'blobfish', 'doctorfish',
    'tilapia', 'kangaroo', 'octopus', 'phoenix', 'aardvark', 'amberjack', 'eel', 'hummingbird',
    'canary', 'hippopotamus', 'snail', 'caterpillar', 'mosquito', 'bat', 'ferret', 'gecko',
    'kudu', 'moose', 'cockroach', 'cricket', 'grasshopper', 'meerkat', 'spider', 'lobster',
    'squid', 'puffin', 'raven', 'kiwi', 'koala', 'wolverine',
    # Set2 animals
    'akita', 'bear', 'camel', 'coyote', 'snake', 'monkey', 'leopard', 'fish', 'ostrich', 'pigeon',
    'dolphin', 'frog', 'goat', 'goose', 'wolf', 'gorilla', 'beaver', 'lizard', 'flamingo', 'swan',
    'elk', 'duck', 'reindeer', 'bison', 'shark', 'mouse', 'owl', 'llama', 'cobra', 'zebra',
    'otter', 'crab', 'peafowl', 'rhino', 'dinosaur', 'dove', 'badger', 'chinchilla', 'cougar',
    'crow', 'seal', 'worm', 'ant', 'bee', 'butterfly', 'dragonfly', 'dragon', 'gadwall', 'mule',
    'liger', 'german shepherd', 'bulldog', 'husky', 'poodle', 'chihuahua', 'dachshund', 'basenji',
    'dalmatian', 'mermaid', 'seahorse', 'fangtooth', 'dugong', 'walrus', 'vampire', 'stork',
    'swallow', 'songbird', 'woodpecker', 'starling', 'mannikin', 'pelikan', 'beetle', 'finch'
]

# List of predicates/relations between entities
Predicates = [
    # Set1 predicates
    'owe money to',
    'give a magnifier to',
    'learn the basics of resource management from',
    'know the defensive plans of',
    'show all her cards to',
    'prepare armor for',
    'sing a victory song for',
    'need support from',
    'respect',
    'raise a peace flag for',
    'become',
    'an enemy of',
    'roll the dice for',
    'hold the same number of points as',
    'offer a job to',
    'wink at',
    'steal five points from',
    'knock down the fortress of',
    'burn the warehouse of',
    'eat the food of',
    'attack the green fields whose owner is',
    'proceed to the spot that is right after the spot of',
    'remove one of the pieces of',
    # Set2 predicates
    'tear down the castle that belongs to',
    'bring an oil tank for',
    'reveal a secret to',
    'enjoy the company of',
    'neglect',
    'want to see',
    'swear to',
    'refuse to help',
    'manage to convince',
    'call',
    'stop the victory of',
    'dance with',
    'shout at',
    'smile at',
    'pay money to',
    'unite with',
    'hug',
    'destroy the wall constructed by',
    'create one castle for',
    'disarm',
    'acquire a photograph of',
    'borrow one of the weapons of',
    'fall on a square of',
    'suspect the truthfulness of',
    'invest in the company whose owner is',
    'leave the houses occupied by',
    'hide the cards that she has from',
    'swim in the pool next to the house of',
    'negotiate a deal with',
    'trade one of its pieces with',
    'build a power plant near the green fields of',
    'take over the emperor of',
    'capture the king of',
    'surrender to'
]


class Predicate:
    def __init__(self, name: str, negated: bool = False):
        self.name = name
        self.negated = negated

    def __str__(self):
        if self.negated:
            return f"does not {self.name}"
        return self.name

    def negate(self):
        return Predicate(self.name, not self.negated)

    def __eq__(self, other):
        return isinstance(other, Predicate) and self.name == other.name and self.negated == other.negated

    def __hash__(self):
        return hash((self.name, self.negated))

    def __repr__(self):
        return f"Predicate(name={self.name}, negated={self.negated})"


class Statement:
    def __init__(self, subject: str, predicate: Predicate, obj: str):
        self.subject = subject
        self.predicate = predicate
        self.object = obj

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"

    def negate(self):
        return Statement(self.subject, self.predicate.negate(), self.object)

    def __eq__(self, other):
        return (
            isinstance(other, Statement)
            and self.subject == other.subject
            and self.predicate == other.predicate
            and self.object == other.object
        )

    def __hash__(self):
        return hash((self.subject, self.predicate, self.object))

    def __repr__(self):
        return (
            f"Statement(subject={repr(self.subject)}, "
            f"predicate={repr(self.predicate)}, object={repr(self.object)})"
        )


class Rule:
    def __init__(self, type_id: int, conditions: List[Statement], conclusion: Statement, rule_id: int = -1):
        self.type_id = type_id
        self.conditions = conditions
        self.conclusion = conclusion
        self.rule_id = rule_id

    def __str__(self):
        if self.type_id == 0:
            assert len(self.conditions) == 1, repr(self)
            _, p1, e1 = (
                self.conditions[0].subject,
                self.conditions[0].predicate,
                self.conditions[0].object,
            )
            _, p2, e2 = self.conclusion.subject, self.conclusion.predicate, self.conclusion.object
            return f"If any animal {p1} {e1}, then it {p2} {e2}"
        if self.type_id == 1:
            assert len(self.conditions) == 2, repr(self)
            _, p1, e1 = (
                self.conditions[0].subject,
                self.conditions[0].predicate,
                self.conditions[0].object,
            )
            _, p2, e2 = (
                self.conditions[1].subject,
                self.conditions[1].predicate,
                self.conditions[1].object,
            )
            _, p3, e3 = self.conclusion.subject, self.conclusion.predicate, self.conclusion.object
            return f"If any animal {p1} {e1} and {p2} {e2}, then it {p3} {e3}"
        if self.type_id == 2:
            assert len(self.conditions) == 1, repr(self)
            e1, p1, e2 = (
                self.conditions[0].subject,
                self.conditions[0].predicate,
                self.conditions[0].object,
            )
            e2_again, p2, e3 = self.conclusion.subject, self.conclusion.predicate, self.conclusion.object
            assert e2_again == e2
            return f"If {e1} {p1} {e2}, then {e2} {p2} {e3}"
        if self.type_id == 3:
            assert len(self.conditions) == 2, repr(self)
            e1, p1, e2 = (
                self.conditions[0].subject,
                self.conditions[0].predicate,
                self.conditions[0].object,
            )
            e3, p2, e2_again = (
                self.conditions[1].subject,
                self.conditions[1].predicate,
                self.conditions[1].object,
            )
            assert e2 == e2_again
            e2_final, p3, e4 = self.conclusion.subject, self.conclusion.predicate, self.conclusion.object
            assert e2_final == e2
            return f"If {e1} {p1} {e2} and {e3} {p2} {e2}, then {e2} {p3} {e4}"
        if self.type_id == 4:
            assert len(self.conditions) == 1, repr(self)
            _, p1, e1 = (
                self.conditions[0].subject,
                self.conditions[0].predicate,
                self.conditions[0].object,
            )
            e2, p2, e3 = self.conclusion.subject, self.conclusion.predicate, self.conclusion.object
            return f"If there exists an animal which {p1} {e1}, then {e2} {p2} {e3}"
        raise ValueError(f"Invalid type_id: {self.type_id}")

    def __repr__(self):
        return (
            f"Rule(type_id={self.type_id}, conditions={repr(self.conditions)}, "
            f"conclusion={repr(self.conclusion)}, rule_id={self.rule_id})"
        )


class RuleGenerator:
    def __init__(self, prob_negate: float = 0.5):
        self.prob_negate = prob_negate
        self.generator_fn = {
            0: self.generate_from_question_0,
            1: self.generate_from_question_1,
            2: self.generate_from_question_2,
            3: self.generate_from_question_3,
            4: self.generate_from_question_4,
        }

    def generate_from_question(self, q: Statement, type_id: int = -1) -> Tuple[List[Statement], Rule]:
        if type_id == -1:
            type_id = random.randint(0, 4)
        states = self.generator_fn[type_id](q)
        return states, Rule(type_id, copy.deepcopy(states), q)

    def sample_predicate(self, n: int = 1):
        ps = [Predicate(p) for p in random.sample(Predicates, n)]
        ps = [p if random.random() < self.prob_negate else p.negate() for p in ps]
        if len(ps) == 1:
            return ps[0]
        return ps

    def sample_subject(self, n: int = 1):
        es = random.sample(Entities, n)
        if len(es) == 1:
            return es[0]
        return es

    def sample_object(self, n: int = 1):
        es = random.sample(Entities, n)
        if len(es) == 1:
            return es[0]
        return es

    def generate_from_question_0(self, q: Statement) -> List[Statement]:
        x, _, _ = q.subject, q.predicate, q.object
        p1 = self.sample_predicate()
        e1 = self.sample_object()
        return [Statement(x, p1, e1)]

    def generate_from_question_1(self, q: Statement) -> List[Statement]:
        x, _, _ = q.subject, q.predicate, q.object
        p1, p2 = self.sample_predicate(2)
        e1, e2 = self.sample_object(2)
        return [Statement(x, p1, e1), Statement(x, p2, e2)]

    def generate_from_question_2(self, q: Statement) -> List[Statement]:
        e2, _, _ = q.subject, q.predicate, q.object
        p1 = self.sample_predicate()
        e1 = self.sample_object()
        return [Statement(e1, p1, e2)]

    def generate_from_question_3(self, q: Statement) -> List[Statement]:
        e2, _, _ = q.subject, q.predicate, q.object
        e1, e3 = self.sample_object(2)
        p1, p2 = self.sample_predicate(2)
        return [Statement(e1, p1, e2), Statement(e3, p2, e2)]

    def generate_from_question_4(self, q: Statement) -> List[Statement]:
        e2, _, _ = q.subject, q.predicate, q.object
        x, e1 = self.sample_subject(2)
        p1 = self.sample_predicate()
        return [Statement(x, p1, e1)]


class BbehBoardgameCaseBuilder:
    def __init__(
        self,
        min_depth: int = 1,
        max_depth: int = 3,
        prob_conflict: float = 0.5,
        prob_conflict_type: float = 0.5,
        prob_negate: float = 0.5,
        answer_distribution: Dict[str, float] | None = None,
    ):
        if min_depth < 1:
            raise ValueError("min_depth must be >= 1")
        if max_depth < min_depth:
            raise ValueError("max_depth must be >= min_depth")
        self.max_depth = max_depth
        self.min_depth = min_depth
        self.prob_conflict = prob_conflict
        self.prob_conflict_type = prob_conflict_type
        self.rule_generator = RuleGenerator(prob_negate)
        self.answer_choices, self.answer_weights = self._normalize_answer_distribution(answer_distribution)

    @staticmethod
    def _normalize_answer_distribution(distribution: Dict[str, float] | None) -> tuple[list[str], list[float] | None]:
        allowed_answers = ['proved', 'disproved', 'unknown']
        if not distribution:
            return allowed_answers, None

        filtered = [(ans, weight) for ans, weight in distribution.items() if ans in allowed_answers and weight > 0]
        if not filtered:
            return allowed_answers, None

        answers, weights = zip(*filtered)
        total = sum(weights)
        normalized_weights = [w / total for w in weights]
        return list(answers), normalized_weights

    def generate_case(self) -> Dict[str, Any]:
        depth = random.randint(self.min_depth, self.max_depth)
        e1 = self.rule_generator.sample_subject()
        p1 = self.rule_generator.sample_predicate()
        e2 = self.rule_generator.sample_object()
        question_statement = Statement(e1, p1, e2)

        case = {
            "facts": [],
            "rules": [],
            "preference_graph": {},
            "question": None,
            "depth": depth,
            "answer": None,
        }

        if self.answer_weights is None:
            answer = random.choice(['proved', 'disproved', 'unknown'])
        else:
            answer = random.choices(self.answer_choices, weights=self.answer_weights, k=1)[0]
        case['answer'] = answer
        case['need_remove'] = answer == 'unknown'

        if answer == 'disproved':
            question_statement = question_statement.negate()

        case['question'] = self.construct_question(question_statement)
        self._generate_theory(case, question_statement, depth)
        case['facts'] = [str(f) for f in case['facts']]
        case['rules'] = {r.rule_id: str(r) for r in case['rules']}
        identity = {
            "facts": case["facts"],
            "rules": case["rules"],
            "preference_graph": case["preference_graph"],
            "question": case["question"],
            "answer": case["answer"],
            "depth": case["depth"],
        }
        return identity

    def construct_prompt(self, identity: Dict[str, Any]) -> str:
        components = [
            "A few players are playing a boardgame. The current state of the game is as follows:",
        ]
        components.extend(f"- {fact}" for fact in identity.get("facts", []))
        components.append("\nThe rules of the game are as follows:")
        rules = identity.get("rules", {})
        components.extend(f"{rule_id}: {text}" for rule_id, text in rules.items())
        components.append("\nRule priorities (higher priority first):")
        preference_graph = identity.get("preference_graph", {})
        components.extend(
            f"> {sup} has precedence over {inf}"
            for sup in preference_graph
            for inf in preference_graph[sup]
        )
        components.append(f"\nQuestion: {identity.get('question')}")
        components.append(
            "\nAnswer must be placed within [answer] tags, exactly one of: proved, disproved, unknown."
        )
        return "\n".join(components)

    def _generate_theory(self, case: Dict[str, Any], statement: Statement, depth: int) -> None:
        def add_rule(rule: Rule):
            rule.rule_id = str(len(case["rules"]))
            case["rules"].append(rule)

        if case['need_remove']:
            if random.random() < 1 / (depth + 1):
                case['need_remove'] = False
                return

        if depth == 0:
            case["facts"].append(statement)
            return

        states, rule = self.rule_generator.generate_from_question(statement)
        add_rule(rule)

        if random.random() < self.prob_conflict:
            neg_statement = statement.negate()
            new_states, new_rule = self.rule_generator.generate_from_question(neg_statement)
            add_rule(new_rule)
            if random.random() < self.prob_conflict_type:
                states += new_states
                case["preference_graph"].setdefault(rule.rule_id, []).append(new_rule.rule_id)
            else:
                random.shuffle(new_states)
                states += new_states[1:]
                case["preference_graph"].setdefault(new_rule.rule_id, []).append(rule.rule_id)

        for state in states:
            self._generate_theory(case, state, depth - 1)

    @staticmethod
    def construct_question(statement: Statement) -> str:
        return f"does the {statement.subject} {statement.predicate} the {statement.object}?"


class BbehBoardgameQAInstructionGenerator(BaseInstructionGenerator):
    """InternBootcamp v2 指令生成器，实现 BBEH boardgame QA 任务"""

    def __init__(
        self,
        min_depth: int = 1,
        max_depth: int = 3,
        prob_conflict: float = 0.5,
        prob_conflict_type: float = 0.5,
        prob_negate: float = 0.5,
        answer_distribution: Dict[str, float] | None = None,
    ):
        super().__init__()
        self.case_builder = BbehBoardgameCaseBuilder(
            min_depth=min_depth,
            max_depth=max_depth,
            prob_conflict=prob_conflict,
            prob_conflict_type=prob_conflict_type,
            prob_negate=prob_negate,
            answer_distribution=answer_distribution,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)

