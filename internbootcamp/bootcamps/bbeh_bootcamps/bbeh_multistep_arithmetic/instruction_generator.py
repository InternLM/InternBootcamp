import math
import random
import re
from typing import Any, Dict, List, Optional

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class MultistepArithmeticCaseBuilder:
    """生成多步自定义算术运算任务的题目与答案。"""

    _DEFAULT_SYMBOLS: List[str] = [
        "><",
        ";",
        "][",
        "@",
        "#",
        "<>",
        "~",
        "&",
        "[]",
        ":",
        "!*",
        "::",
        "^&",
    ]

    def __init__(
        self,
        num_operators: int = 5,
        max_depth: int = 10,
        reuse_prob: float = 0.0,
        operand_min: int = -10,
        operand_max: int = 10,
        seed: Optional[int] = None,
    ) -> None:
        if num_operators < 1:
            raise ValueError("num_operators 必须为正整数。")
        if max_depth < 1:
            raise ValueError("max_depth 必须不小于 1。")
        if operand_min >= operand_max:
            raise ValueError("operand_min 必须小于 operand_max。")
        self.num_operators = min(num_operators, len(self._DEFAULT_SYMBOLS))
        self.max_depth = max_depth
        self.reuse_prob = max(0.0, min(reuse_prob, 0.4))
        self.operand_min = operand_min
        self.operand_max = operand_max
        self.rng = random.Random(seed)
        self._op_map: Dict[str, Any] = {}

    @staticmethod
    def _is_prime(value: int) -> bool:
        if value <= 1:
            return False
        if value in (2, 3):
            return True
        if value % 2 == 0:
            return False
        limit = int(math.isqrt(value))
        for factor in range(3, limit + 1, 2):
            if value % factor == 0:
                return False
        return True

    def _randint_non_zero(self) -> int:
        candidates = list(range(self.operand_min, self.operand_max + 1))
        candidates = [val for val in candidates if val != 0]
        return self.rng.choice(candidates)

    def _select_symbols(self) -> List[str]:
        population = self._DEFAULT_SYMBOLS.copy()
        self.rng.shuffle(population)
        return population[: self.num_operators]

    def _generate_operator_def(self, condition_type: str, available_symbols: List[str]) -> tuple[str, str, str]:
        a, b = "a", "b"
        if condition_type == "product_positive":
            condition = f"{a} * {b} > 0"
            true_expr = f"{a} - {b}"
            false_expr = f"{a} + {b}"
        elif condition_type == "a_gt_b":
            condition = f"{a} > {b}"
            true_expr = f"{a} * {b}"
            false_expr = f"{a} - {b}"
        elif condition_type == "prime_condition":
            condition = f"is_prime({a}) or is_prime({b})"
            true_expr = f"min({a}, {b})"
            false_expr = f"max({a}, {b})"
        elif condition_type == "gcd_condition":
            condition = f"math.gcd({a}, {b}) == 1"
            true_expr = f"{a} + {b}"
            false_expr = f"math.gcd({a}, {b})"
        else:
            condition = f"abs({a} - {b}) < 2"
            true_expr = f"{a} * {b}"
            false_expr = f"{a} - {b}"
        if available_symbols and self.reuse_prob > 0.0 and self.rng.random() < self.reuse_prob:
            reused_symbol = self.rng.choice(available_symbols)
            reuse_expr = f"apply_operator('{reused_symbol}', {a}, {b})"
            true_expr = reuse_expr
            if self.rng.random() < 0.5:
                false_expr = reuse_expr
        return condition, true_expr, false_expr

    def _generate_operators(self, symbols: List[str]) -> List[Dict[str, str]]:
        operators: List[Dict[str, str]] = []
        for index, _symbol in enumerate(symbols):
            condition_type = self.rng.choice(
                ["product_positive", "a_gt_b", "prime_condition", "gcd_condition", "abs_diff"]
            )
            condition, true_expr, false_expr = self._generate_operator_def(condition_type, symbols[:index])
            operators.append(
                {
                    "symbol": _symbol,
                    "condition": condition,
                    "true_expr": true_expr,
                    "false_expr": false_expr,
                }
            )
        return operators

    def _generate_operand(self) -> str:
        return str(self._randint_non_zero())

    def _generate_expression(self, symbols: List[str], depth: int) -> str:
        if depth <= 0 or not symbols:
            return self._generate_operand()

        left = self._generate_expression(symbols, depth - 1)
        right = self._generate_operand()

        num_ops = self.rng.randint(1, min(2, len(symbols)))
        composite_ops = "".join(self.rng.choices(symbols, k=num_ops))
        return f"({left} {composite_ops} {right})"

    def _create_operator_func(self, operator: Dict[str, str]):
        condition = operator["condition"]
        true_expr = operator["true_expr"]
        false_expr = operator["false_expr"]

        context = {
            "math": math,
            "is_prime": self._is_prime,
            "apply_operator": self._apply_operator,
        }

        def func(a: float, b: float) -> float:
            a_val = int(a) if isinstance(a, float) and a.is_integer() else a
            b_val = int(b) if isinstance(b, float) and b.is_integer() else b
            local_env = {"a": a_val, "b": b_val, **context}
            try:
                cond = bool(eval(condition, {}, local_env))
            except Exception:
                cond = False

            expr = true_expr if cond else false_expr
            try:
                result = eval(expr, {}, local_env)
            except Exception:
                result = 0
            return float(result)

        return func

    def _eval_expr(self, expression: str, op_map: Dict[str, Any]) -> float:
        expr = expression.replace(" ", "")
        if not expr:
            return 0.0

        sorted_ops = sorted(op_map.keys(), key=len, reverse=True)

        def parse_number(segment: str) -> tuple[float, str]:
            match = re.match(r"^([+-]?\d+)(.*)", segment)
            if not match:
                return 0.0, ""
            return float(match.group(1)), match.group(2)

        def parse_bracket(segment: str) -> tuple[float, str]:
            if not segment.startswith("("):
                return parse_number(segment)
            balance = 1
            idx = 1
            while idx < len(segment) and balance > 0:
                if segment[idx] == "(":
                    balance += 1
                elif segment[idx] == ")":
                    balance -= 1
                idx += 1
            inner_value = evaluate(segment[1 : idx - 1])
            return inner_value, segment[idx:]

        def parse_ops(segment: str) -> tuple[List[str], str]:
            ops: List[str] = []
            idx = 0
            while idx < len(segment):
                matched = False
                for op in sorted_ops:
                    if segment.startswith(op, idx):
                        ops.append(op)
                        idx += len(op)
                        matched = True
                        break
                if not matched:
                    break
            return ops, segment[idx:]

        def evaluate(segment: str) -> float:
            if not segment:
                return 0.0
            left_val, remainder = parse_bracket(segment)
            current = left_val

            while remainder:
                operators, remainder = parse_ops(remainder)
                if not operators:
                    break
                right_val, remainder = parse_bracket(remainder)

                for operator_symbol in operators:
                    operator_func = op_map.get(operator_symbol)
                    if operator_func is None:
                        current = 0.0
                    else:
                        current = operator_func(current, right_val)
            return current

        return evaluate(expr)

    def generate_case(self) -> Dict[str, Any]:
        self._op_map = {}
        symbols = self._select_symbols()
        operators = self._generate_operators(symbols)
        op_map = {op["symbol"]: self._create_operator_func(op) for op in operators}
        self._op_map = op_map

        a_expr = self._generate_expression(symbols, self.max_depth)
        b_expr = self._generate_expression(symbols, self.max_depth)
        c_expr = self._generate_expression(symbols, self.max_depth)

        a_val = self._eval_expr(a_expr, op_map)
        b_val = self._eval_expr(b_expr, op_map)
        c_val = self._eval_expr(c_expr, op_map)

        return {
            "operators": operators,
            "A": a_expr,
            "B": b_expr,
            "C": c_expr,
            "A_val": a_val,
            "B_val": b_val,
            "C_val": c_val,
            "answer": a_val + b_val - c_val,
        }

    def _apply_operator(self, symbol: str, left: float, right: float) -> float:
        operator = self._op_map.get(symbol)
        if operator is None:
            return 0.0
        return operator(left, right)

    @staticmethod
    def construct_prompt(question_case: Dict[str, Any]) -> str:
        operator_lines = [
            f'${op["symbol"]} b$ equals {op["true_expr"]} if {op["condition"]}; otherwise, {op["false_expr"]}'
            for op in question_case.get("operators", [])
        ]
        operators_desc = "\n".join(operator_lines)
        prompt = (
            "Consider the following custom operations:\n\n"
            f"{operators_desc}\n"
            "For brevity, we use $a <op1><op2> b$ to denote $(a <op1> b) <op2> b$. "
            "For example, $4 +* -5$ means $(4 + -5) * -5$.\n"
            f"Let A = {question_case.get('A')}\n"
            f"Let B = {question_case.get('B')}\n"
            f"Let C = {question_case.get('C')}\n"
            "Compute A + B - C. Your final answer must be in number form. "
            "Please put your final answer within [answer] and [/answer] tags."
        )
        return prompt


class BbehMultistepArithmeticInstructionGenerator(BaseInstructionGenerator):
    """BBEH 多步算术任务的指令生成器。"""

    def __init__(
        self,
        num_operators: int = 5,
        max_depth: int = 10,
        reuse_prob: float = 0.0,
        operand_min: int = -10,
        operand_max: int = 10,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.case_builder = MultistepArithmeticCaseBuilder(
            num_operators=num_operators,
            max_depth=max_depth,
            reuse_prob=reuse_prob,
            operand_min=operand_min,
            operand_max=operand_max,
            seed=seed,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)

    @staticmethod
    def extract_output(output: str) -> Optional[float]:
        if not output:
            return None
        matches = re.findall(r"\[answer\](.*?)\[/answer\]", output, flags=re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        candidate = matches[-1].strip()
        try:
            return float(candidate)
        except ValueError:
            return None

    @classmethod
    def _verify_correction(cls, solution: Optional[float], identity: Dict[str, Any]) -> bool:
        if solution is None:
            return False
        expected = identity.get("answer")
        if expected is None:
            return False
        try:
            return abs(float(solution) - float(expected)) < 1e-6
        except (TypeError, ValueError):
            return False


