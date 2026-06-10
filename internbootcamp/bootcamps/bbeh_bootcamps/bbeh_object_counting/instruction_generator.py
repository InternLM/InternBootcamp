import random
from typing import Any, Dict, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class ObjectCountingCaseBuilder:
    """生成 BBEH Object Counting 任务的题目、背景故事与答案。"""

    DEFAULT_CATEGORY_VOCAB: Dict[str, List[str]] = {
        "fruits": [
            "apples",
            "bananas",
            "grapes",
            "lemons",
            "oranges",
            "pears",
            "plums",
            "kiwis",
            "mangoes",
            "pineapples",
            "watermelons",
            "cantaloupes",
            "dates",
            "peaches",
            "strawberries",
            "raspberries",
            "blueberries",
            "blackberries",
            "cherries",
            "pomegranates",
            "lychees",
            "passion fruits",
            "dragonfruits",
            "persimmons",
            "star fruits",
            "jackfruits",
            "custard apples",
            "soursops",
        ],
        "animals/insects": [
            "dogs",
            "cats",
            "elephants",
            "lions",
            "tigers",
            "bears",
            "wolves",
            "zebras",
            "giraffes",
            "monkeys",
            "kangaroos",
            "koalas",
            "pandas",
            "rhinoceroses",
            "hippopotamuses",
            "hyenas",
            "cheetahs",
            "leopards",
            "antelopes",
            "buffaloes",
            "crocodiles",
            "snakes",
            "spiders",
            "bees",
            "mosquitoes",
            "butterflies",
            "dragonflies",
            "scorpions",
            "ladybugs",
            "grasshoppers",
            "crickets",
            "fireflies",
            "cockroaches",
        ],
        "cars": [
            "Toyota Corolla",
            "Honda Civic",
            "Ford Mustang",
            "Chevrolet Silverado",
            "Nissan Altima",
            "Volkswagen Golf",
            "BMW 3 Series",
            "Mercedes-Benz C-Class",
            "Jeep Gladiator",
            "Honda CR-V",
            "Mazda CX-5",
            "Toyota RAV4",
            "Tesla Model 3",
            "Hyundai Tucson",
            "Kia Sportage",
            "Subaru Outback",
            "Ford F-150",
            "Toyota Highlander",
            "Honda Accord",
            "Nissan Rogue",
            "Chevrolet Equinox",
            "Toyota Camry",
            "Hyundai Elantra",
            "Jeep Wrangler",
            "Ford Explorer",
            "Toyota Tacoma",
            "Honda Pilot",
            "Nissan Sentra",
            "Mazda3",
            "Subaru Forester",
        ],
        "mobiles": [
            "iPhone 5",
            "iPhone 7",
            "iPhone 13",
            "iPhone 15",
            "Samsung Galaxy S21",
            "Samsung Galaxy Z Fold6",
            "Huawei P40",
            "Huawei Pura 70 Ultra",
            "Google Pixel 6",
            "OnePlus 9",
            "Xiaomi Mi 11",
            "Sony Xperia",
            "LG Velvet",
            "Motorola Edge",
            "Huawei Nova 11 SE",
            "Samsung Galaxy A35",
            "Google Pixel 7a",
            "Xiaomi Redmi Note 13",
            "Oppo Reno 10",
            "Vivo V30 Pro",
            "Realme GT 6",
            "Nokia X30",
            "Asus Zenfone 11",
            "iPhone X",
            "Samsung Galaxy C55",
            "Huawei Mate 70",
            "Google Pixel 8 Pro",
        ],
        "musical instruments": [
            "grand piano",
            "acoustic guitar",
            "electric guitar",
            "violin",
            "cello",
            "double bass",
            "flute",
            "clarinet",
            "saxophone",
            "trumpet",
            "trombone",
            "french horn",
            "tuba",
            "drum set",
            "conga drums",
            "bongo drums",
            "marimba",
            "xylophone",
            "harp",
            "ukulele",
            "mandolin",
            "banjo",
            "accordion",
            "harmonica",
            "sitar",
            "oud",
            "didgeridoo",
            "kalimba",
            "theremin",
            "synthesizer",
        ],
    }

    DEFAULT_PEOPLE = [
        "grandmother",
        "grandfather",
        "mother",
        "father",
        "sister",
        "brother",
        "uncle",
        "aunt",
        "cousin",
        "friend",
        "neighbor",
        "colleague",
        "classmate",
        "roommate",
        "neighbor",
        "colleague",
        "classmate",
        "roommate",
    ]

    DEFAULT_ENDINGS = [
        "and after double-checking the numbers I am confident in this total",
        "and following an audit this is the final count I kept",
        "and after all the changes this is where things settled",
        "and in the end this is the amount that remains with me",
    ]

    def __init__(
        self,
        categories: List[str] | None = None,
        min_items: int = 3,
        max_items: int = 7,
        min_count: int = 5,
        max_count: int = 200,
        max_other_items: int = 8,
        max_other_people: int = 15,
        rng: random.Random | None = None,
    ):
        if min_items <= 0 or max_items < min_items:
            raise ValueError("min_items 与 max_items 参数非法")
        if min_count <= 0 or max_count < min_count:
            raise ValueError("min_count 与 max_count 参数非法")
        self.rng = rng or random.Random()
        self.categories = categories or [
            "fruits",
            "animals/insects",
            "cars",
            "mobiles",
            "musical instruments",
        ]
        self.min_items = min_items
        self.max_items = max_items
        self.min_count = min_count
        self.max_count = max_count
        self.max_other_items = max_other_items
        self.max_other_people = max_other_people

    def _choice(self, seq):
        return self.rng.choice(seq)

    def _randint(self, low: int, high: int) -> int:
        return self.rng.randint(low, high)

    def _generate_story(self, target: int) -> str:
        """生成一段包含增减变化且最终落在 target 的库存故事。"""
        initial_low = max(1, target - 80)
        initial_high = target + 80 if target + 80 > initial_low else initial_low + 20
        initial = self._randint(initial_low, initial_high)

        current = initial
        parts = [f"initially I had {initial}"]

        for _ in range(2):
            if current <= 1:
                op = "gain"
            else:
                op = self._choice(["gain", "loss"])

            delta = self._randint(1, max(3, current // 2 + 1))
            if op == "gain":
                current += delta
                parts.append(f"then I got {delta} more")
            else:
                delta = min(delta, current - 1)
                current -= delta
                parts.append(f"then I lost {delta}")

        if current == target:
            delta = self._randint(1, 5)
            current += delta
            parts.append(f"then I got {delta} more")

        if current < target:
            delta = target - current
            current = target
            parts.append(f"then I got {delta} more")
        elif current > target:
            delta = current - target
            current = target
            parts.append(f"then I lost {delta}")

        ending = self._choice(self.DEFAULT_ENDINGS)
        return f"({', '.join(parts)}, {ending}, so I now have {target})"

    def _generate_category_items(self, category: str) -> Tuple[List[str], int]:
        item_count = self._randint(self.min_items, self.max_items)
        entries: List[str] = []
        total = 0

        vocab = self.DEFAULT_CATEGORY_VOCAB.get(category, [])
        if not vocab:
            raise ValueError(f"Category {category} 缺少词汇表")

        for _ in range(item_count):
            number = self._randint(self.min_count, self.max_count)
            item = self._choice(vocab)
            story = self._generate_story(number)
            entries.append(f"I have {number} {item} {story}.")
            total += number
        return entries, total

    def _generate_other_items(self, excluded: set[str]) -> List[str]:
        other_entries: List[str] = []
        for category in self.categories:
            if category in excluded:
                continue
            vocab = self.DEFAULT_CATEGORY_VOCAB.get(category, [])
            other_samples = self._randint(0, self.max_other_items)
            for _ in range(other_samples):
                number = self._randint(1, self.max_count)
                item = self._choice(vocab)
                other_entries.append(f"I have {number} {item} {self._generate_story(number)}.")
        return other_entries

    def _generate_other_people_items(self) -> List[str]:
        entries: List[str] = []
        total_people = self._randint(max(3, self.max_other_people // 2), self.max_other_people)
        for _ in range(total_people):
            person = self._choice(self.DEFAULT_PEOPLE)
            category = self._choice(self.categories)
            vocab = self.DEFAULT_CATEGORY_VOCAB.get(category, [])
            number = self._randint(1, 300)
            item = self._choice(vocab)
            entries.append(f"My {person} has {number} {item}.")
        return entries

    def generate_case(self) -> Dict[str, Any]:
        """构建一个包含库存描述、目标类别和答案的完整案例。"""
        cat1, cat2 = self.rng.sample(self.categories, 2)
        operation = self._choice(["sum", "difference"])

        primary_items_1, total_1 = self._generate_category_items(cat1)
        primary_items_2, total_2 = self._generate_category_items(cat2)

        other_entries = self._generate_other_items({cat1, cat2})
        people_entries = self._generate_other_people_items()

        inventory = primary_items_1 + primary_items_2 + other_entries + people_entries
        self.rng.shuffle(inventory)

        if operation == "sum":
            answer = total_1 + total_2
            op_description = "sum"
        else:
            answer = abs(total_1 - total_2)
            op_description = "absolute difference"

        return {
            "items": inventory,
            "categories": [cat1, cat2],
            "operation": operation,
            "operation_description": op_description,
            "answer": answer,
            "totals": {
                cat1: total_1,
                cat2: total_2,
            },
        }

    @staticmethod
    def construct_prompt(identity: Dict[str, Any]) -> str:
        categories = identity.get("categories", [])
        if len(categories) != 2:
            raise ValueError("案例缺少目标类别信息")
        cat1, cat2 = categories
        operation_description = identity.get("operation_description", "sum")
        inventory = identity.get("items", [])

        examples_1 = ", ".join(ObjectCountingCaseBuilder.DEFAULT_CATEGORY_VOCAB.get(cat1, [])[:3])
        examples_2 = ", ".join(ObjectCountingCaseBuilder.DEFAULT_CATEGORY_VOCAB.get(cat2, [])[:3])
        inventory_block = "\n".join(inventory)

        prompt_lines = [
            "You are an inventory analyst tasked with interpreting a long log of possessions.",
            f"Focus exclusively on the items that belong to the categories {cat1} and {cat2}.",
            "",
            "Rules:",
            f"1. Items considered {cat1} include examples like {examples_1}.",
            f"2. Items considered {cat2} include examples like {examples_2}.",
            "3. Ignore quantities owned by other people; only count the first-person statements.",
            "4. Each sentence already reflects the final quantity after the story in parentheses.",
            "5. Provide numeric reasoning if needed, but the final answer must be a single number.",
            "",
            "Inventory Log:",
            inventory_block,
            "",
            f"Task: compute the {operation_description} of the total counts for my {cat1} and {cat2}.",
            "Return your final answer using [answer]NUMBER[/answer] format.",
        ]
        return "\n".join(prompt_lines)


class BbehObjectCountingInstructionGenerator(BaseInstructionGenerator):
    """BBEH Object Counting 任务的指令生成器。"""

    def __init__(
        self,
        categories: List[str] | None = None,
        min_items: int = 3,
        max_items: int = 7,
        min_count: int = 5,
        max_count: int = 200,
        max_other_items: int = 8,
        max_other_people: int = 15,
        seed: int | None = None,
    ):
        super().__init__()
        rng = random.Random(seed) if seed is not None else None
        self.case_builder = ObjectCountingCaseBuilder(
            categories=categories,
            min_items=min_items,
            max_items=max_items,
            min_count=min_count,
            max_count=max_count,
            max_other_items=max_other_items,
            max_other_people=max_other_people,
            rng=rng,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)

