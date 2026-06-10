import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class DyckLanguageCaseBuilder:
    """负责生成 Dyck 括号校验任务的题设与提示文本。"""

    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 20,
        error_prob: float = 0.8,
        rng: Optional[random.Random] = None,
    ):
        if min_length < 2:
            raise ValueError("min_length 必须不小于 2")
        if max_length < min_length:
            raise ValueError("max_length 必须大于等于 min_length")
        if not 0 <= error_prob <= 1:
            raise ValueError("error_prob 必须位于 [0, 1] 区间")

        self.min_length = min_length
        self.max_length = max_length
        self.error_prob = error_prob
        self.rng = rng or random.Random()

        self.bracket_pairs: Dict[str, str] = {'(': ')', '[': ']', '{': '}', '<': '>'}
        self.open_brackets: set[str] = set(self.bracket_pairs.keys())
        self.close_brackets: set[str] = set(self.bracket_pairs.values())

    def _random(self) -> float:
        return self.rng.random()

    def _choice(self, seq: Sequence[Any]) -> Any:
        return self.rng.choice(seq)

    def _randint(self, low: int, high: int) -> int:
        return self.rng.randint(low, high)

    def _generate_valid_sequence(self) -> Tuple[str, List[str]]:
        stack: List[str] = []
        sequence: List[str] = []
        steps: List[str] = [
            "Thought 1: We should process each input one by one and keep track of the stack configuration.",
            "Thought 2: stack: empty",
        ]
        current_stack: List[str] = []

        length_target = self._randint(self.min_length, self.max_length)

        while len(sequence) < length_target:
            if not stack or (self._random() < 0.6 and len(sequence) < length_target - len(stack)):
                bracket = self._choice(tuple(self.bracket_pairs.keys()))
                sequence.append(bracket)
                stack.append(bracket)
                current_stack.append(bracket)
            else:
                open_bracket = stack.pop()
                close_bracket = self.bracket_pairs[open_bracket]
                sequence.append(close_bracket)
                if current_stack:
                    current_stack.pop()

            step_num = len(steps) + 1
            stack_str = ' '.join(current_stack) if current_stack else 'empty'
            steps.append(f"Thought {step_num}: {sequence[-1]} ; stack: {stack_str}")

            if len(sequence) >= self.min_length and not stack and self._random() < 0.3:
                break

        return ''.join(sequence), steps

    def _inject_error(self, steps: List[str], input_seq: str) -> Tuple[Optional[int], Optional[str]]:
        error_funcs = [
            (self._corrupt_stack_state, "corrupt_stack_state"),
            (self._swap_bracket_type, "swap_bracket_type"),
            (self._skip_closing, "skip_closing"),
            (self._incorrect_stack_update, "incorrect_stack_update"),
            (self._misinterpret_input, "misinterpret_input"),
        ]

        error_func, error_type = self._choice(error_funcs)
        error_step = error_func(steps, input_seq)
        if error_step is None:
            return None, None
        return error_step, error_type

    def _corrupt_stack_state(self, steps: List[str], *_: Any) -> Optional[int]:
        valid_steps = [idx for idx in range(5, len(steps)) if '; stack:' in steps[idx]]
        if not valid_steps:
            return None

        step_idx = self._choice(valid_steps)
        step = steps[step_idx]

        parts = step.split(';')
        stack_desc = parts[1].split(': ')[-1]
        new_stack = self._modify_stack_description(stack_desc)
        steps[step_idx] = f"{parts[0]}; stack: {new_stack}"
        return step_idx + 1

    def _modify_stack_description(self, stack_desc: str) -> str:
        if stack_desc == 'empty':
            return self._choice(tuple(self.open_brackets))

        elements = stack_desc.split()
        error_type = self._randint(1, 4)

        if error_type == 1 and elements:
            remove_idx = self._randint(0, len(elements) - 1)
            remaining = elements[:remove_idx] + elements[remove_idx + 1:]
            return ' '.join(remaining) or 'empty'
        if error_type == 2:
            new_element = self._choice(tuple(self.open_brackets))
            insert_idx = self._randint(0, len(elements))
            new_elements = elements[:insert_idx] + [new_element] + elements[insert_idx:]
            return ' '.join(new_elements)
        if error_type == 3 and len(elements) >= 2:
            idx1, idx2 = self.rng.sample(range(len(elements)), 2)
            elements[idx1], elements[idx2] = elements[idx2], elements[idx1]
            return ' '.join(elements)

        if not elements:
            return self._choice(tuple(self.open_brackets))
        replace_idx = self._randint(0, len(elements) - 1)
        current = elements[replace_idx]
        candidates = [b for b in self.open_brackets if b != current]
        if candidates:
            elements[replace_idx] = self._choice(tuple(candidates))
        return ' '.join(elements) if elements else 'empty'

    def _swap_bracket_type(self, steps: List[str], input_seq: str) -> Optional[int]:
        close_positions = [(idx, ch) for idx, ch in enumerate(input_seq) if ch in self.close_brackets]
        if not close_positions:
            return None

        pos, original = self._choice(close_positions)
        step_idx = pos + 2
        if step_idx >= len(steps):
            return None

        candidates = [c for c in self.close_brackets if c != original]
        if not candidates:
            return None

        new_char = self._choice(tuple(candidates))
        parts = steps[step_idx].split(';')
        steps[step_idx] = f"Thought {step_idx + 1}: {new_char} ;{parts[1]}"
        return step_idx + 1

    def _skip_closing(self, steps: List[str], *_: Any) -> Optional[int]:
        close_steps = [
            (idx, step)
            for idx, step in enumerate(steps)
            if idx > 2 and any(ch in step.split(';')[0] for ch in self.close_brackets)
        ]
        if not close_steps:
            return None

        step_idx, step = self._choice(close_steps)
        parts = step.split(';')
        stack_desc = parts[1].split(': ')[-1]
        if stack_desc != 'empty':
            steps[step_idx] = f"{parts[0]};{parts[1]}"
            return step_idx + 1
        return None

    def _incorrect_stack_update(self, steps: List[str], *_: Any) -> Optional[int]:
        valid_steps = [idx for idx in range(5, len(steps) - 1) if '; stack:' in steps[idx]]
        if not valid_steps:
            return None

        step_idx = self._choice(valid_steps)
        current_step = steps[step_idx]
        next_step = steps[step_idx + 1]

        current_parts = current_step.split(';')
        current_stack = current_parts[1].split(': ')[-1]

        next_parts = next_step.split(';')
        next_bracket = next_parts[0].split()[-1]

        if next_bracket in self.open_brackets:
            if self._random() < 0.5:
                steps[step_idx + 1] = f"{next_parts[0]}; stack: {current_stack}"
            else:
                wrong_bracket_candidates = [b for b in self.open_brackets if b != next_bracket]
                wrong_bracket = self._choice(tuple(wrong_bracket_candidates)) if wrong_bracket_candidates else next_bracket
                if current_stack == 'empty':
                    steps[step_idx + 1] = f"{next_parts[0]}; stack: {wrong_bracket}"
                else:
                    steps[step_idx + 1] = f"{next_parts[0]}; stack: {current_stack} {wrong_bracket}"
        elif next_bracket in self.close_brackets and current_stack != 'empty':
            stack_elements = current_stack.split()
            if not stack_elements:
                return step_idx + 2
            if self._random() < 0.5 and len(stack_elements) > 1:
                wrong_idx = self._randint(0, len(stack_elements) - 2)
                new_stack = stack_elements[:wrong_idx] + stack_elements[wrong_idx + 1:]
                steps[step_idx + 1] = f"{next_parts[0]}; stack: {' '.join(new_stack) or 'empty'}"
            else:
                steps[step_idx + 1] = f"{next_parts[0]}; stack: {current_stack}"

        return step_idx + 2

    def _misinterpret_input(self, steps: List[str], _input_seq: str) -> Optional[int]:
        valid_steps = [idx for idx in range(3, min(8, len(steps))) if '; stack:' in steps[idx]]
        if not valid_steps:
            return None

        step_idx = self._choice(valid_steps)
        parts = steps[step_idx].split(';')
        current_bracket = parts[0].split()[-1]
        all_brackets = tuple(self.open_brackets | self.close_brackets)

        candidates = [b for b in all_brackets if b != current_bracket]
        if not candidates:
            return None

        new_bracket = self._choice(tuple(candidates))
        steps[step_idx] = f"Thought {step_idx + 1}: {new_bracket} ;{parts[1]}"
        return step_idx + 1

    def _propagate_error_effects(self, steps: List[str], error_step: int) -> None:
        error_idx = error_step - 1
        if error_idx < 0 or error_idx >= len(steps) or '; stack:' not in steps[error_idx]:
            return

        parts = steps[error_idx].split(';')
        error_stack = parts[1].split(': ')[-1]

        for idx in range(error_idx + 1, len(steps)):
            if '; stack:' not in steps[idx]:
                continue

            current_parts = steps[idx].split(';')
            bracket = current_parts[0].split()[-1]

            if bracket in self.open_brackets:
                error_stack = bracket if error_stack == 'empty' else f"{error_stack} {bracket}"
            elif bracket in self.close_brackets and error_stack != 'empty':
                elements = error_stack.split()
                if elements:
                    elements.pop()
                    error_stack = ' '.join(elements) or 'empty'

            steps[idx] = f"{current_parts[0]}; stack: {error_stack}"

    def _add_conclusion_step(self, steps: List[str]) -> None:
        if any("So the answer is" in step for step in steps):
            return

        last_stack = "empty"
        for step in reversed(steps):
            if '; stack:' in step:
                last_stack = step.split('; stack: ')[-1]
                break

        step_num = len(steps) + 1
        if last_stack == "empty":
            steps.append(f"Thought {step_num}: Now, we have reached the end. The final stack is empty.")
            steps.append(f"Thought {step_num + 1}: So the answer is empty")
        else:
            steps.append(f"Thought {step_num}: Now, we have reached the end. The final stack is \"{last_stack}\".")
            stack_elements = last_stack.split()
            if stack_elements:
                pop_description = ", ".join(f"\"{elem}\"" for elem in reversed(stack_elements))
                steps.append(f"Thought {step_num + 1}: We will need to pop out {pop_description} one by one in that order.")
            closing_brackets = [self.bracket_pairs.get(elem, ')') for elem in reversed(stack_elements)]
            closing_sequence = ' '.join(closing_brackets)
            needed_brackets = ", ".join(f"\"{b}\"" for b in closing_brackets)
            steps.append(f"Thought {step_num + 2}: So, we need {needed_brackets}. So the answer is {closing_sequence}")

    def generate_case(self) -> Dict[str, Any]:
        input_seq, correct_steps = self._generate_valid_sequence()
        modified_steps = list(correct_steps)
        error_step: Optional[int] = None
        error_type: Optional[str] = None

        if self._random() < self.error_prob:
            candidate_step, candidate_type = self._inject_error(modified_steps, input_seq)
            if candidate_step is not None:
                error_step = candidate_step
                error_type = candidate_type
                self._propagate_error_effects(modified_steps, error_step)

        self._add_conclusion_step(modified_steps)
        return {
            "input_sequence": input_seq,
            "correct_steps": correct_steps,
            "modified_steps": modified_steps,
            "error_step": error_step,
            "error_type": error_type,
        }

    def construct_prompt(self, identity: Dict[str, Any]) -> str:
        input_sequence = identity.get("input_sequence", "")
        steps = '\n'.join(identity.get("modified_steps", []))
        prompt_templates = [
            f"""Dyck语言是计算机科学中的一种形式语言，由匹配的括号对组成。你是一个Dyck语言的专家，擅长分析括号序列中可能出现的错误。在这个任务中，你需要分析括号序列的处理过程，并找出其中的第一个错误步骤。

## 输入序列
{input_sequence}

## 分析步骤
{steps}

## 你的任务
请仔细检查上述步骤，找出第一个出现错误的步骤编号。如果所有步骤都正确，请回答"No"。

请逐步推理解答此问题，并且将最终答案放入[answer] and [/answer]中。例如：
[answer]
步骤编号或"No"
[/answer]""",
            f"""你是一个Dyck语言的专家。Dyck语言是计算机科学中的一种形式语言，由匹配的括号对组成。给定一个括号序列和对应于处理该序列的思考步骤，请你找出其中的第一个错误步骤。

## 括号序列
{input_sequence}

## 处理过程
{steps}

## 分析要求
1. 每个开括号必须与对应类型的闭括号匹配
2. 括号必须按"后开先闭"原则匹配
3. 堆栈状态必须准确反映当前未匹配的开括号

## 请回答
如果发现错误，请指出第一个错误步骤的编号；如果全部正确，请回答"No"。

请逐步推理解答此问题，并且将最终答案放入[answer] and [/answer]中。例如：
[answer]
你的答案
[/answer]""",
            f"""You are given a bracket sequence and the reasoning steps for processing it, find the first erroneous step, if any.

## Sequence
{input_sequence}

## Processing
{steps}

## Analysis Requirements
1. Each opening bracket must match with its corresponding closing bracket
2. Brackets must follow the "last-opened-first-closed" principle
3. Stack state must accurately reflect currently unmatched opening brackets

## Response Format
Identify the number of the first incorrect step, or answer "No" if all steps are correct.
Please follow the format below:
[answer]
Your answer here
[/answer]
Please think step by step.""",
            f"""You are debugging an algorithm that processes bracket sequences according to Dyck language rules. The algorithm tracks a stack of open brackets and pops them when matching closing brackets are encountered. Your task is to identify the first step where the algorithm makes a mistake in processing the sequence.

## Given Sequence
{input_sequence}

## Algorithm Trace
{steps}

Please think step by step and put your final answer within [answer] and [/answer] tags.
For example:
[answer]
First error step number or "No" if error-free
[/answer]
Now generate your solution.""",
            f"""You are an expert in a language called Dyck where you must complete sequences of unmatched brackets (e.g., [], {{}}, <>). You are given a Dyck language sequence and the thoughts that were used to reason about it. Your job is to identify the first thought that goes wrong, if any.

## Sequence
{input_sequence}

## Thoughts
{steps}

If there is a mistake, respond with the step number (e.g., "7"). If no mistake exists, answer "No".
Please solve this task step by step and put your final answer within [answer] and [/answer] tags.""",
        ]

        return self._choice(prompt_templates)


class BbehDyckLanguagesInstructionGenerator(BaseInstructionGenerator):
    """BBEH Dyck Languages 任务的指令生成器。"""

    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 20,
        error_prob: float = 0.8,
        seed: Optional[int] = None,
    ):
        super().__init__()
        rng = random.Random(seed) if seed is not None else random.Random()
        self.case_builder = DyckLanguageCaseBuilder(
            min_length=min_length,
            max_length=max_length,
            error_prob=error_prob,
            rng=rng,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)


