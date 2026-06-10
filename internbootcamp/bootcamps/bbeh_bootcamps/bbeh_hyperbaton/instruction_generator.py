from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


Option = Tuple[str, bool]


@dataclass
class HyperbatonConfig:
    min_example_sentences: int = 80
    max_example_sentences: int = 160
    min_full_examples: int = 30
    min_partial_examples: int = 40
    num_options: int = 10
    min_correct_options: int = 3
    max_correct_options: int = 6
    max_regenerate_attempts: int = 128


class HyperbatonCaseBuilder:
    """生成形容词顺序（Hyperbaton）任务的题目与标准答案。"""

    ADJECTIVE_TYPES: Sequence[str] = (
        "age",
        "quality",
        "size",
        "shape",
        "color",
        "material",
        "nationality",
        "activity",
    )

    ADJECTIVES: Dict[str, Sequence[str]] = {
        "age": ("old", "new", "ancient", "old-fashioned", "brand-new", "archaic"),
        "quality": (
            "good",
            "terrible",
            "lovely",
            "awful",
            "nice",
            "wonderful",
            "repulsive",
            "obnoxious",
            "mysterious",
            "ridiculous",
            "silly",
        ),
        "size": (
            "big",
            "small",
            "tiny",
            "enormous",
            "huge",
            "massive",
            "large",
            "little",
            "medium-size",
            "midsize",
            "normal-size",
        ),
        "shape": (
            "square",
            "circular",
            "triangular",
            "rectangular",
            "spherical",
            "pyramidal",
            "prismlike",
        ),
        "color": (
            "red",
            "blue",
            "green",
            "yellow",
            "black",
            "white",
            "cyan",
            "magenta",
            "violet",
            "brown",
            "gray",
            "pink",
            "crimson",
            "indigo",
            "maroon",
            "teal",
            "aqua",
        ),
        "material": (
            "wood",
            "plastic",
            "steel",
            "iron",
            "glass",
            "paper",
            "cloth",
            "cardboard",
            "rubber",
            "leather",
            "wool",
            "fiberglass",
        ),
        "nationality": (
            "chinese",
            "american",
            "russian",
            "japanese",
            "vietnamese",
            "iranian",
            "turkish",
            "mexican",
            "brazilian",
            "german",
            "filipino",
            "ethiopian",
            "indian",
            "egyptian",
            "nigerian",
            "thai",
            "indonesian",
            "congolese",
            "bangladeshi",
            "pakistani",
        ),
        "activity": (
            "smoking",
            "hiking",
            "driving",
            "walking",
            "eating",
            "drinking",
            "typing",
            "whittling",
            "snorkeling",
            "exercise",
        ),
    }

    NOUNS: Sequence[str] = (
        "ball",
        "box",
        "bag",
        "chair",
        "table",
        "car",
        "book",
        "pen",
        "pencil",
        "bottle",
        "cup",
        "knife",
        "fork",
        "spoon",
        "plate",
        "flower pot",
        "hat",
        "shirt",
        "shoe",
        "guitar",
        "piano",
        "clock",
        "watch",
        "camera",
        "phone",
        "computer",
        "sofa",
        "bed",
        "lamp",
        "umbrella",
        "car key",
        "wallet",
        "necklace",
        "ring",
        "earring",
        "brush",
        "scissors",
        "candle",
        "vase",
        "banana",
        "apple",
        "dog",
        "bird",
        "hammer",
        "drill",
        "screwdriver",
        "plier",
        "stapler",
        "ruler",
        "calculator",
        "saw",
        "trash can",
        "fire extinguisher",
        "wrench",
        "bicycle",
        "speaker",
        "marker",
        "toolbox",
        "jar",
        "bowl",
        "sunglasses",
        "canvas",
        "key",
        "house",
        "pencil",
        "tool",
    )

    def __init__(self, *, seed: int | None = None, config: HyperbatonConfig | None = None) -> None:
        self.rng = random.Random(seed)
        self.standard_order = list(self.ADJECTIVE_TYPES)
        self.config = config or HyperbatonConfig()

    def _choice(self, seq: Sequence[Any]) -> Any:
        return self.rng.choice(seq)

    def _randint(self, low: int, high: int) -> int:
        return self.rng.randint(low, high)

    def _sample(self, population: Sequence[Any], k: int) -> List[Any]:
        if k >= len(population):
            return list(population)
        return self.rng.sample(list(population), k)

    def generate_example_sentence(self, noun: str, num_adjectives: int, use_partial: bool) -> str:
        if use_partial:
            available_types = self._sample(self.standard_order, min(num_adjectives, len(self.standard_order)))
        else:
            end_idx = self._randint(num_adjectives, len(self.standard_order))
            available_types = self.standard_order[:end_idx]

        adjectives: List[str] = []
        for adj_type in available_types:
            candidates = self.ADJECTIVES.get(adj_type, ())
            if candidates:
                adjectives.append(self._choice(candidates))
        adjectives = adjectives[:num_adjectives]

        if not adjectives:
            adj_type = self._choice(self.standard_order)
            adjectives.append(self._choice(self.ADJECTIVES[adj_type]))

        return " ".join(adjectives) + f" {noun}"

    def generate_example_sentences(self, total_sentences: int) -> List[str]:
        sentences: List[str] = []

        def append_sentence(sentence: str) -> None:
            if sentence not in sentences:
                sentences.append(sentence)

        for _ in range(self.config.min_full_examples):
            noun = self._choice(self.NOUNS)
            num_adjectives = self._randint(3, 5)
            append_sentence(self.generate_example_sentence(noun, num_adjectives, use_partial=False))

        for _ in range(self.config.min_partial_examples):
            noun = self._choice(self.NOUNS)
            num_adjectives = self._randint(2, 4)
            append_sentence(self.generate_example_sentence(noun, num_adjectives, use_partial=True))

        while len(sentences) < total_sentences:
            noun = self._choice(self.NOUNS)
            num_adjectives = self._randint(1, 5)
            use_partial = bool(self._randint(0, 1))
            append_sentence(self.generate_example_sentence(noun, num_adjectives, use_partial))

        self.rng.shuffle(sentences)
        return sentences

    def _build_correct_sentence(self, num_adjectives: int) -> str:
        selected_types = self.standard_order[:num_adjectives]
        words = [self._choice(self.ADJECTIVES[adj_type]) for adj_type in selected_types]
        noun = self._choice(self.NOUNS)
        return " ".join(words + [noun])

    def _build_incorrect_sentence(self, num_adjectives: int) -> str:
        selected_types = self._sample(self.standard_order, num_adjectives)
        self.rng.shuffle(selected_types)
        while selected_types == list(self.standard_order[: num_adjectives]):
            self.rng.shuffle(selected_types)
        words = [self._choice(self.ADJECTIVES[adj_type]) for adj_type in selected_types]
        noun = self._choice(self.NOUNS)
        return " ".join(words + [noun])

    def generate_options(self, num_options: int) -> List[Option]:
        num_correct = self._randint(self.config.min_correct_options, self.config.max_correct_options)
        num_correct = min(num_correct, num_options - 1)

        options: List[Option] = []
        seen_sentences: set[str] = set()

        def add_sentence(sentence: str, is_correct: bool) -> None:
            if sentence in seen_sentences:
                return
            options.append((sentence, is_correct))
            seen_sentences.add(sentence)

        while sum(1 for _, flag in options if flag) < num_correct:
            sentence = self._build_correct_sentence(self._randint(3, 7))
            add_sentence(sentence, True)

        while len(options) < num_options:
            sentence = self._build_incorrect_sentence(self._randint(3, 7))
            add_sentence(sentence, False)

        self.rng.shuffle(options)
        return options[:num_options]

    @staticmethod
    def format_options(options: Iterable[Option]) -> Tuple[List[str], str]:
        formatted: List[str] = []
        correct_letters: List[str] = []
        for idx, (sentence, is_correct) in enumerate(options):
            label = chr(ord("A") + idx)
            formatted.append(f"({label}) {sentence}")
            if is_correct:
                correct_letters.append(label)
        answer = "".join(sorted(correct_letters)) if correct_letters else "K"
        return formatted, answer

    def _build_prompt(self, examples: Sequence[str], formatted_options: Sequence[str]) -> str:
        examples_text = " ".join(f"{sentence}" for sentence in examples)
        options_text = " ".join(formatted_options)
        prompt = (
            "In a variant of English, we are given that the following sentences have correct adjective order:\n"
            f"{examples_text}\n\n"
            "In this variant of English, which of the following sentences (Options A-J) use the correct adjective order? "
            "If none of the sentences (Options A-J) use the correct adjective order, select option K. Select all that apply.\n"
            f"{options_text}\n"
            "(K) None of the above\n\n"
            "Provide your final answer as a concatenation of all the correct choices. "
            'For example, if B and C have correct adjective order, then your final answer must be "BC".'
        )
        return prompt

    def generate_case(self) -> Dict[str, Any]:
        for _ in range(self.config.max_regenerate_attempts):
            total_examples = self._randint(
                self.config.min_example_sentences,
                self.config.max_example_sentences,
            )
            examples = self.generate_example_sentences(total_examples)

            options = self.generate_options(self.config.num_options)
            formatted_options, answer = self.format_options(options)

            example_set = set(examples)
            option_sentences = {opt.split(") ", 1)[1] for opt in formatted_options}

            if example_set.intersection(option_sentences):
                continue
            if "CEJ" in answer:
                continue

            prompt = self._build_prompt(examples, formatted_options)
            return {"input": prompt, "target": answer}

        raise RuntimeError("Failed to generate a valid hyperbaton case within the allowed attempts.")


class BbehHyperbatonInstructionGenerator(BaseInstructionGenerator):
    """BBEH Hyperbaton 任务的指令生成器。"""

    def __init__(self, seed: int | None = None, **kwargs: Any) -> None:
        super().__init__()
        config = HyperbatonConfig(**{k: v for k, v in kwargs.items() if k in HyperbatonConfig().__dict__})
        self.case_builder = HyperbatonCaseBuilder(seed=seed, config=config)

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        base_prompt = identity.get("input", "")
        if not base_prompt:
            return (
                "你是一名擅长分析英语形容词顺序的语言学助手。"
                "请阅读题目给出的示例和备选项，判断哪些句子符合形容词顺序规则，"
                "最后按照“最终答案: ”后接大写字母组合的格式作答，例如“最终答案: BD”或“最终答案: K”。"
            )

        guidance = (
            "\n\n请仔细分析示例中的形容词顺序规律，判断哪些选项符合该规律。"
            "在完整推理后，以“最终答案: ”紧跟正确选项字母（如“BDF”或“K”）结束回答。"
        )
        return base_prompt + guidance


