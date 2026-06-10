import random
from typing import Any, Dict, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class BooleanExpressionCaseBuilder:
    """生成布尔表达式推理任务的题目与答案。"""

    def __init__(self, max_depth: int = 5, num_choices: int = 5, rng: random.Random | None = None):
        if num_choices < 2:
            raise ValueError("num_choices 必须不小于 2")
        self.max_depth = max_depth
        self.num_choices = num_choices
        self.rng = rng or random.Random()
        self.capital_facts = {
            'Afghanistan': 'Kabul',
            'Armenia': 'Yerevan',
            'Azerbaijan': 'Baku',
            'Belarus': 'Minsk',
            'Cameroon': 'Yaounde',
            'Canada': 'Ottawa',
            'Colombia': 'Bogota',
            'Denmark': 'Copenhagen',
            'Gambia': 'Banjul',
            'Germany': 'Berlin',
            'India': 'New Delhi',
            'Iran': 'Tehran',
            'Iraq': 'Baghdad',
            'Jordan': 'Amman',
            'Malaysia': 'Kuala Lumpur',
            'Nepal': 'Kathmandu',
            'Nigeria': 'Abuja',
            'Norway': 'Oslo',
            'Turkey': 'Ankara',
        }
        self.false_capitals = {
            'Afghanistan': ['Kandahar', 'Herat'],
            'Armenia': ['Gyumri', 'Vanadzor'],
            'Azerbaijan': ['Ganja', 'Sumqayit'],
            'Belarus': ['Grodno', 'Brest'],
            'Cameroon': ['Douala', 'Garoua'],
            'Canada': ['Toronto', 'Vancouver'],
            'Colombia': ['Medellin', 'Cali'],
            'Denmark': ['Aarhus', 'Odense'],
            'Gambia': ['Libreville', 'Serrekunda'],
            'Germany': ['Munich', 'Hamburg'],
            'India': ['Mumbai', 'Delhi'],
            'Iran': ['Isfahan', 'Shiraz'],
            'Iraq': ['Basra', 'Mosul'],
            'Jordan': ['Beirut', 'Zarqa'],
            'Malaysia': ['Putrajaya', 'Johor Bahru'],
            'Nepal': ['Pokhara', 'Bhaktapur'],
            'Nigeria': ['Lagos', 'Kano'],
            'Norway': ['Bergen', 'Trondheim'],
            'Turkey': ['Istanbul', 'Izmir'],
        }

    def _randint(self, low: int, high: int) -> int:
        return self.rng.randint(low, high)

    def _choice(self, seq):
        return self.rng.choice(seq)

    def _generate_math_expression(self) -> str:
        a = self._randint(-10, 10)
        b = self._randint(-10, 10)
        c = self._randint(-10, 10) or 1  # 避免除以 0
        d = self._randint(-10, 10)
        template = self._choice([
            f"{a} * {b} + {c} * {d} is less than or equal to {self._randint(-10, 10)} * {self._randint(-10, 10)}",
            f"{a} * {b} > {c}",
            f"{a} - ({b} / {c}) is greater than {d}",
            f"{a} - ({b} / {c}) <= {d}",
            f"max({a}, {b}, {c}, {d}) - min({a}, {b}, {c}, {d}) is greater than {self._randint(1, 10)}",
            f"max({a}, {b}, {c}, {d}) - min({a}, {b}, {c}, {d}) <= {self._randint(1, 10)}",
        ])
        return template

    def _generate_capital_fact(self, is_true: bool) -> str:
        country = self._choice(list(self.capital_facts.keys()))
        if is_true:
            capital = self.capital_facts[country]
        else:
            capital = self._choice(self.false_capitals[country])
        return f"The capital of {country} is {capital}."

    def _generate_atomic_expr(self, target_value: bool | None = None):
        if target_value is None:
            return self._choice([True, False])

        expr_type = self._choice(['bool', 'capital', 'math'])
        if target_value:
            if expr_type == 'bool':
                return "True"
            if expr_type == 'capital':
                return self._generate_capital_fact(is_true=True)
            a = self._randint(1, 10)
            return f"{a} * {a} > {a}"

        if expr_type == 'bool':
            return "False"
        if expr_type == 'capital':
            return self._generate_capital_fact(is_true=False)
        a = self._randint(1, 10)
        return f"{a} * {-a} > {a * a}"

    def _generate_expression(self, depth: int = 0, target_value: bool | None = None) -> Tuple[str, bool]:
        if depth >= self.max_depth or self.rng.random() < 0.3:
            if isinstance(target_value, bool):
                expr = self._generate_atomic_expr(target_value)
                return str(expr), target_value
            val = bool(self.rng.getrandbits(1))
            expr = self._generate_atomic_expr(val)
            return str(expr), val

        operator = self._choice(['and', 'or', 'not'])
        if operator == 'not':
            sub_target = (not target_value) if isinstance(target_value, bool) else bool(self.rng.getrandbits(1))
            sub_expr, sub_val = self._generate_expression(depth + 1, sub_target)
            return f"not ({sub_expr})", (not sub_val)

        if operator == 'and':
            if target_value:
                left_target, right_target = True, True
            else:
                if self.rng.random() < 0.5:
                    left_target, right_target = False, self._choice([True, False])
                else:
                    left_target, right_target = self._choice([True, False]), False
        else:  # or
            if target_value:
                if self.rng.random() < 0.5:
                    left_target, right_target = True, self._choice([True, False])
                else:
                    left_target, right_target = self._choice([True, False]), True
            else:
                left_target, right_target = False, False

        left_expr, left_val = self._generate_expression(depth + 1, left_target)
        right_expr, right_val = self._generate_expression(depth + 1, right_target)
        if operator == 'and':
            result_val = left_val and right_val
        else:
            result_val = left_val or right_val
        return f"({left_expr}) {operator} ({right_expr})", result_val

    def _generate_complex_expression(self, target_value: bool) -> Tuple[str, bool]:
        expr, actual_val = self._generate_expression(0, target_value)
        if self.rng.random() < 0.7:
            for _ in range(self._randint(1, 3)):
                expr = f"not not {expr}"
        return expr, actual_val

    def generate_case(self) -> Dict[str, Any]:
        expressions: list[str] = []
        answer_index = self._randint(0, self.num_choices - 1)
        for idx in range(self.num_choices):
            target_value = idx == answer_index
            expr, val = self._generate_complex_expression(target_value)
            attempts = 0
            while val != target_value and attempts < 5:
                expr, val = self._generate_complex_expression(target_value)
                attempts += 1
            expressions.append(str(expr))
        return {
            "expressions": expressions,
            "answer": answer_index,
        }

    @staticmethod
    def construct_prompt(identity: Dict[str, Any]) -> str:
        expressions = identity.get("expressions", [])
        prompt_lines = [
            "Exactly one of the following boolean expressions evaluates to True.",
            "Evaluate carefully and identify which expression is True.",
            "",
        ]
        for idx, expr in enumerate(expressions):
            label = chr(ord("A") + idx)
            prompt_lines.append(f"({label}) {expr}")
        prompt_lines.append("")
        prompt_lines.append(
            "Return your conclusion using [answer]X[/answer] format where X is the letter of the true expression."
        )
        return "\n".join(prompt_lines)


class BbehBooleanExpressionsInstructionGenerator(BaseInstructionGenerator):
    """BBEH boolean expressions 任务的指令生成器，实现题目与提示文本输出。"""

    def __init__(self, max_depth: int = 5, num_choices: int = 5, seed: int | None = None):
        super().__init__()
        rng = random.Random(seed) if seed is not None else None
        self.case_builder = BooleanExpressionCaseBuilder(
            max_depth=max_depth,
            num_choices=num_choices,
            rng=rng,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)

