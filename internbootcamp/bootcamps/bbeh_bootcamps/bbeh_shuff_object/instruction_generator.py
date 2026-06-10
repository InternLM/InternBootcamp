from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


BASE_COLORS = [
    "amber",
    "amethyst",
    "apricot",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "black",
    "blue",
    "brass",
    "bronze",
    "burgundy",
    "chartreuse",
    "chocolate",
    "cobalt",
    "coffee",
    "coral",
    "crimson",
    "cyan",
    "denim",
    "emerald",
    "fuchsia",
    "gold",
    "gray",
    "green",
    "indigo",
    "ivory",
    "jade",
    "lavender",
    "lemon",
    "lime",
    "magenta",
    "maroon",
    "mint",
    "navy",
    "ochre",
    "olive",
    "orange",
    "peach",
    "periwinkle",
    "pink",
    "plum",
    "purple",
    "rose",
    "ruby",
    "saffron",
    "salmon",
    "scarlet",
    "silver",
    "tan",
    "teal",
    "turquoise",
    "violet",
    "white",
    "yellow",
]

COLOR_ADJECTIVES = [
    "bright",
    "deep",
    "light",
    "dark",
    "pastel",
    "vivid",
    "soft",
    "muted",
    "radiant",
    "metallic",
    "faded",
    "glowing",
    "neon",
    "frosted",
    "dusky",
    "saturated",
]

COLOR_SUFFIXES = [
    "gloss",
    "sheen",
    "shade",
    "glow",
    "tint",
    "tone",
    "spark",
    "flare",
    "shine",
    "gleam",
    "mist",
    "haze",
]

COLOR_LIBRARY = list(
    dict.fromkeys(
        BASE_COLORS
        + [
            f"{adj} {color}"
            for adj in COLOR_ADJECTIVES
            for color in BASE_COLORS
        ]
        + [
            f"{color} {suffix}"
            for color in BASE_COLORS
            for suffix in COLOR_SUFFIXES
        ]
    )
)

BOOK_TITLE_ADJECTIVES = [
    "Ancient",
    "Hidden",
    "Forgotten",
    "Enchanted",
    "Silent",
    "Golden",
    "Midnight",
    "Crystal",
    "Scarlet",
    "Shadow",
    "Emerald",
    "Whispering",
    "Timeless",
    "Endless",
    "Wandering",
    "Radiant",
    "Mystic",
    "Secret",
    "Boundless",
    "Celestial",
]

BOOK_TITLE_NOUNS = [
    "Kingdom",
    "Voyage",
    "Chronicle",
    "Legacy",
    "Labyrinth",
    "Garden",
    "Storm",
    "Oath",
    "Prophecy",
    "Quest",
    "Empire",
    "Song",
    "Alliance",
    "Rebellion",
    "Cipher",
    "Codex",
    "Tower",
    "Mirror",
    "Dream",
    "Oracle",
]

BOOK_TITLE_PLACES = [
    "Avalon",
    "Eldoria",
    "Solstice",
    "Midgard",
    "Elysium",
    "Arcanum",
    "Luminara",
    "Nocturne",
    "Astralis",
    "Horizon",
    "Mythos",
    "Aurora",
    "Obsidian",
    "Valeria",
    "Celestia",
]

BOOK_LIBRARY = list(
    dict.fromkeys(
        [
            f"The {adj} {noun}"
            for adj in BOOK_TITLE_ADJECTIVES
            for noun in BOOK_TITLE_NOUNS
        ]
        + [
            f"{adj} {noun}"
            for adj in BOOK_TITLE_ADJECTIVES
            for noun in BOOK_TITLE_NOUNS
        ]
        + [
            f"{noun} of {place}"
            for noun in BOOK_TITLE_NOUNS
            for place in BOOK_TITLE_PLACES
        ]
        + [
            f"Chronicles of {place}"
            for place in BOOK_TITLE_PLACES
        ]
    )
)

SOCCER_VARIANTS = [
    f"{role} #{idx}"
    for idx in range(1, 33)
    for role in [
        "goalkeeper",
        "defender",
        "midfielder",
        "forward",
        "striker",
        "left wing",
        "right wing",
        "center back",
        "sweeper",
        "libero",
        "wingback",
        "holding midfielder",
        "attacking midfielder",
        "center forward",
        "false nine",
    ]
]

SQUARE_PARTNER_LABELS = [
    f"partner {letter}{suffix}"
    for suffix in ["", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for letter in [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]
]


class ShuffObjectCaseBuilder:
    """构建 BBEH Shuffle Object 任务案例与题面。"""

    DEFAULT_CONTEXTS = [
        "game of catch",
        "gift exchange",
        "soccer match",
        "book exchange",
        "square dance",
    ]

    OBJECT_POOLS = {
        "game of catch": [
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "orange",
            "pink",
            "brown",
            "black",
            "white",
        ],
        "gift exchange": [
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "orange",
            "pink",
            "brown",
            "black",
            "white",
        ],
        "soccer match": [
            "goalkeeper",
            "defender",
            "midfielder",
            "forward",
            "striker",
            "left wing",
            "right wing",
            "center back",
            "sweeper",
            "libero",
        ],
        "book exchange": [
            "Catch-22",
            "1984",
            "To Kill a Mockingbird",
            "The Great Gatsby",
            "Brave New World",
            "Pride and Prejudice",
            "The Catcher in the Rye",
            "Moby Dick",
            "War and Peace",
            "The Hobbit",
        ],
        "square dance": [
            f"partner {chr(ord('A') + i)}" for i in range(10)
        ],
    }

    BASE_COLORS = [
        "amber",
        "amethyst",
        "apricot",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "black",
        "blue",
        "brass",
        "bronze",
        "burgundy",
        "chartreuse",
        "chocolate",
        "cobalt",
        "coffee",
        "coral",
        "crimson",
        "cyan",
        "denim",
        "emerald",
        "fuchsia",
        "gold",
        "gray",
        "green",
        "indigo",
        "ivory",
        "jade",
        "lavender",
        "lemon",
        "lime",
        "magenta",
        "maroon",
        "mint",
        "navy",
        "ochre",
        "olive",
        "orange",
        "peach",
        "periwinkle",
        "pink",
        "plum",
        "purple",
        "rose",
        "ruby",
        "saffron",
        "salmon",
        "scarlet",
        "silver",
        "tan",
        "teal",
        "turquoise",
        "violet",
        "white",
        "yellow",
    ]

    COLOR_ADJECTIVES = [
        "bright",
        "deep",
        "light",
        "dark",
        "pastel",
        "vivid",
        "soft",
        "muted",
        "radiant",
        "metallic",
        "faded",
        "glowing",
        "neon",
        "frosted",
        "dusky",
        "saturated",
    ]

    COLOR_SUFFIXES = [
        "gloss",
        "sheen",
        "shade",
        "glow",
        "tint",
        "tone",
        "spark",
        "flare",
        "shine",
        "gleam",
        "mist",
        "haze",
    ]

    COLOR_LIBRARY = list(
        dict.fromkeys(
            BASE_COLORS
            + [
                f"{adj} {color}"
                for adj in COLOR_ADJECTIVES
                for color in BASE_COLORS
            ]
            + [
                f"{color} {suffix}"
                for color in BASE_COLORS
                for suffix in COLOR_SUFFIXES
            ]
        )
    )

    BOOK_TITLE_ADJECTIVES = [
        "Ancient",
        "Hidden",
        "Forgotten",
        "Enchanted",
        "Silent",
        "Golden",
        "Midnight",
        "Crystal",
        "Scarlet",
        "Shadow",
        "Emerald",
        "Whispering",
        "Timeless",
        "Endless",
        "Wandering",
        "Radiant",
        "Mystic",
        "Secret",
        "Boundless",
        "Celestial",
    ]

    BOOK_TITLE_NOUNS = [
        "Kingdom",
        "Voyage",
        "Chronicle",
        "Legacy",
        "Labyrinth",
        "Garden",
        "Storm",
        "Oath",
        "Prophecy",
        "Quest",
        "Empire",
        "Song",
        "Alliance",
        "Rebellion",
        "Cipher",
        "Codex",
        "Tower",
        "Mirror",
        "Dream",
        "Oracle",
    ]

    BOOK_TITLE_PLACES = [
        "Avalon",
        "Eldoria",
        "Solstice",
        "Midgard",
        "Elysium",
        "Arcanum",
        "Luminara",
        "Nocturne",
        "Astralis",
        "Horizon",
        "Mythos",
        "Aurora",
        "Obsidian",
        "Valeria",
        "Celestia",
    ]

    BOOK_LIBRARY = list(
        dict.fromkeys(
            [
                f"The {adj} {noun}"
                for adj in BOOK_TITLE_ADJECTIVES
                for noun in BOOK_TITLE_NOUNS
            ]
            + [
                f"{adj} {noun}"
                for adj in BOOK_TITLE_ADJECTIVES
                for noun in BOOK_TITLE_NOUNS
            ]
            + [
                f"{noun} of {place}"
                for noun in BOOK_TITLE_NOUNS
                for place in BOOK_TITLE_PLACES
            ]
            + [
                f"Chronicles of {place}"
                for place in BOOK_TITLE_PLACES
            ]
        )
    )

    SOCCER_VARIANTS = [
        f"{role} #{idx}"
        for idx in range(1, 33)
        for role in [
            "goalkeeper",
            "defender",
            "midfielder",
            "forward",
            "striker",
            "left wing",
            "right wing",
            "center back",
            "sweeper",
            "libero",
            "wingback",
            "holding midfielder",
            "attacking midfielder",
            "center forward",
            "false nine",
        ]
    ]

    SQUARE_PARTNER_LABELS = [
        f"partner {letter}{suffix}"
        for suffix in ["", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for letter in [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
    ]

    PEOPLE_POOL = [
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Heidi",
        "Ivan",
        "Judy",
        "Larry",
        "Mary",
        "Nancy",
        "Oliver",
        "Patty",
        "Quincy",
        "Rachel",
        "Steve",
        "Tina",
        "Ulysses",
        "Victoria",
        "Wendy",
        "Xavier",
        "Yvonne",
        "Zachary",
        "Ada",
        "Bertha",
        "Clara",
        "Diana",
        "Eleanor",
        "Fiona",
        "Gina",
        "Hannah",
        "Irene",
        "Julia",
        "Kate",
        "Laura",
        "Mia",
        "Nina",
        "Olivia",
        "Penelope",
        "Quinn",
        "Rosa",
        "Sophia",
        "Tara",
        "Ursula",
        "Vera",
        "Xenia",
        "Yara",
        "Zara",
        "Abel",
        "Bianca",
        "Carter",
        "Derek",
        "Elena",
        "Felix",
        "Georgia",
        "Harper",
        "Isabel",
        "Jonah",
        "Kendra",
        "Lewis",
        "Miles",
        "Noah",
        "Opal",
        "Paula",
        "Reid",
        "Selena",
        "Trent",
        "Uma",
        "Valerie",
        "Ximena",
        "Yosef",
        "Zoe",
        "Aaron",
        "Abigail",
        "Adrian",
        "Aiden",
        "Alana",
        "Albert",
        "Alexa",
        "Alfred",
        "Allison",
        "Amber",
        "Amy",
        "Andre",
        "Angela",
        "Anita",
        "Annette",
        "Anthony",
        "April",
        "Ariana",
        "Arnold",
        "Arthur",
        "Ashley",
        "Austin",
        "Autumn",
        "Avery",
        "Bailey",
        "Barbara",
        "Beatrice",
        "Benjamin",
        "Bethany",
        "Beverly",
        "Blaine",
        "Blake",
        "Bonnie",
        "Bradley",
        "Brandon",
        "Brian",
        "Brianna",
        "Brooke",
        "Bryce",
        "Caleb",
        "Calvin",
        "Camila",
        "Candice",
        "Cara",
        "Carla",
        "Carlos",
        "Carmen",
        "Caroline",
        "Cassandra",
        "Catherine",
        "Cecilia",
        "Cedric",
        "Celeste",
        "Chad",
        "Charlotte",
        "Cheryl",
        "Chris",
        "Christian",
        "Christina",
        "Christine",
        "Claire",
        "Claudia",
        "Clive",
        "Colin",
        "Connor",
        "Cooper",
        "Courtney",
        "Craig",
        "Damian",
        "Damon",
        "Danielle",
        "Darius",
        "Dean",
        "Denise",
        "Dennis",
        "Desmond",
        "Dexter",
        "Dillon",
        "Dominic",
        "Donna",
        "Dorothy",
        "Douglas",
        "Edgar",
        "Edith",
        "Edmund",
        "Eduardo",
        "Edward",
        "Eli",
        "Elijah",
        "Elisa",
        "Elise",
        "Eliza",
        "Elizabeth",
        "Elliot",
        "Eloise",
        "Elsa",
        "Emerson",
        "Emilia",
        "Emily",
        "Emma",
        "Eric",
        "Erica",
        "Erik",
        "Erin",
        "Esther",
        "Ethan",
        "Eugene",
        "Evan",
        "Faith",
        "Felicia",
        "Fernanda",
        "Floyd",
        "Frances",
        "Frederick",
        "Gabriel",
        "Gabriela",
        "Gail",
        "Garrett",
        "Gavin",
        "Gemma",
        "George",
        "Gerald",
        "Gloria",
        "Gordon",
        "Gregory",
        "Gwendolyn",
        "Hailey",
        "Haley",
        "Hector",
        "Helen",
        "Henry",
        "Holly",
        "Hudson",
        "Hugo",
        "Ian",
        "Ingrid",
        "Iris",
        "Isaac",
        "Isla",
        "Jack",
        "Jackson",
        "Jacob",
        "Jacqueline",
        "Jade",
        "James",
        "Jamie",
        "Janelle",
        "Jared",
        "Jasmine",
        "Jason",
        "Javier",
        "Jeffery",
        "Jennifer",
        "Jeremy",
        "Jerome",
        "Jessica",
        "Jillian",
        "Joanna",
        "Jocelyn",
        "Joel",
        "Jordan",
        "Jose",
        "Joseph",
        "Josie",
        "Joyce",
        "Judith",
        "Justin",
        "Kara",
        "Karen",
        "Karina",
        "Karissa",
        "Karl",
        "Katelyn",
        "Kathleen",
        "Kathryn",
        "Katrina",
        "Kayla",
        "Keith",
        "Kelly",
        "Kevin",
        "Kimberly",
        "Kirk",
        "Kristen",
        "Kristin",
        "Kyle",
        "Lance",
        "Lara",
        "Lauren",
        "Leah",
        "Leon",
        "Leonard",
        "Liam",
        "Lillian",
        "Lily",
        "Lincoln",
        "Lindsay",
        "Logan",
        "Loretta",
        "Lorraine",
        "Lucas",
        "Luis",
        "Luke",
        "Luna",
        "Luther",
        "Lydia",
        "Mabel",
        "Mackenzie",
        "Madeline",
        "Madison",
        "Maggie",
        "Malcolm",
        "Marcus",
        "Margaret",
        "Maria",
        "Marian",
        "Marilyn",
        "Marlene",
        "Marshall",
        "Martha",
        "Martin",
        "Marvin",
        "Mason",
        "Matilda",
        "Megan",
        "Melanie",
        "Melissa",
        "Micah",
        "Michael",
        "Michelle",
        "Miguel",
        "Mindy",
        "Miranda",
        "Molly",
        "Monica",
        "Morgan",
        "Naomi",
        "Natalie",
        "Nathan",
        "Nathaniel",
        "Neil",
        "Nelson",
        "Nicholas",
        "Nicole",
        "Nigel",
        "Nora",
        "Norman",
        "Omar",
        "Ophelia",
        "Oscar",
        "Owen",
        "Pamela",
        "Patricia",
        "Patrick",
        "Paulina",
        "Pauline",
        "Pearl",
        "Pedro",
        "Peter",
        "Phillip",
        "Phoebe",
        "Piper",
        "Preston",
        "Quentin",
        "Quinton",
        "Rafael",
        "Ralph",
        "Ramona",
        "Randall",
        "Rebecca",
        "Reece",
        "Regina",
        "Renee",
        "Ricardo",
        "Richard",
        "Riley",
        "Rita",
        "Robert",
        "Robin",
        "Roger",
        "Ronald",
        "Rory",
        "Rose",
        "Ruben",
        "Ruby",
        "Russell",
        "Ruth",
        "Sabrina",
        "Samuel",
        "Sandra",
        "Sara",
        "Scarlett",
        "Scott",
        "Sebastian",
        "Serena",
        "Shannon",
        "Sharon",
        "Sheila",
        "Shelby",
        "Simon",
        "Spencer",
        "Stacey",
        "Stanley",
        "Stella",
        "Stephanie",
        "Stephen",
        "Stewart",
        "Sydney",
        "Sylvia",
        "Tabitha",
        "Tamara",
        "Tanya",
        "Taylor",
        "Teresa",
        "Theodore",
        "Theresa",
        "Thomas",
        "Timothy",
        "Tobias",
        "Todd",
        "Tracy",
        "Trevor",
        "Tristan",
        "Tyler",
        "Valentina",
        "Vanessa",
        "Vaughn",
        "Veronica",
        "Victor",
        "Vincent",
        "Violet",
        "Virginia",
        "Vivian",
        "Walter",
        "Wayne",
        "Wesley",
        "Whitney",
        "Wilfred",
        "William",
        "Willow",
        "Wilson",
        "Winifred",
        "Wyatt",
        "Xander",
        "Xiomara",
        "Yasmine",
        "Yolanda",
        "Yvette",
        "Zachariah",
        "Zane",
        "Zelda",
        "Zion",
    ]

    def __init__(
        self,
        min_people: int = 3,
        max_people: int = 5,
        context_type: Optional[str] = None,
        object_pool_size: int = 10,
        seed: Optional[int] = None,
    ) -> None:
        if min_people <= 1:
            raise ValueError("min_people 必须大于 1。")
        if max_people < min_people:
            raise ValueError("max_people 必须不小于 min_people。")
        if object_pool_size <= 1:
            raise ValueError("object_pool_size 必须大于 1。")
        if object_pool_size < max_people:
            raise ValueError("object_pool_size 不能小于 max_people。")

        self.min_people = min_people
        self.max_people = max_people
        self.context_type = context_type
        self.object_pool_size = object_pool_size
        self.rng = random.Random(seed) if seed is not None else random.Random()

    # ------------------------------------------------------------------ #
    # 公开接口
    # ------------------------------------------------------------------ #
    def generate_case(self) -> Dict[str, Any]:
        people = self._generate_people_names()
        context_type = self._select_context_type()
        object_pool = self._build_object_pool(context_type)
        objects = self.rng.sample(object_pool, len(people))

        initial_assignments = dict(zip(people, objects))
        swaps = self._generate_valid_swaps(people)

        final_state = dict(initial_assignments)
        for a, b in swaps:
            final_state[a], final_state[b] = final_state[b], final_state[a]

        question_person = self.rng.choice(people)

        return {
            "people": people,
            "context_type": context_type,
            "object_pool": object_pool,
            "initial_assignments": initial_assignments,
            "swaps": swaps,
            "question_person": question_person,
            "correct_answer": final_state[question_person],
        }

    @staticmethod
    def construct_prompt(identity: Dict[str, Any]) -> str:
        context_type = identity["context_type"]
        templates = {
            "game of catch": (
                "In a game of catch, {people_list} each have a ball of different colors. "
                "Initially: {initial_desc}.\n"
                "Swaps:\n{swaps_desc}\n"
                "After all swaps, which ball does {target} have? "
                "Please solve this task step by step and put your answer(the color) within <answer></answer>.\n"
            ),
            "gift exchange": (
                "During a gift exchange: {people_list} received gifts. "
                "Initial gifts: {initial_desc}.\n"
                "Swaps:\n{swaps_desc}\n"
                "After swapping, what gift does {target} have? "
                "Please solve this task step by step and put your answer(the color) within <answer></answer>.\n"
            ),
            "soccer match": (
                "In a soccer match positions: {people_list}. "
                "Initial positions: {initial_desc}.\n"
                "Position swaps:\n{swaps_desc}\n"
                "What position does {target} play finally? "
                "Please solve this task step by step and put your answer(the soccer) within <answer></answer>.\n"
            ),
            "book exchange": (
                "Friends swapped books: {people_list}. "
                "Initial books: {initial_desc}.\n"
                "Book swaps:\n{swaps_desc}\n"
                "What book does {target} end up with? "
                "Please solve this task step by step and put your answer(the book) within <answer></answer>.\n"
            ),
            "square dance": (
                "Square dance partners: {people_list}. "
                "Initial partners: {initial_desc}.\n"
                "Partner swaps:\n{swaps_desc}\n"
                "Who is {target}'s final partner? "
                "Please solve this task step by step and put your answer(the final partner's name) within <answer></answer>.\n"
            ),
        }

        verbs = {
            "game of catch": "swap balls",
            "gift exchange": "swap gifts",
            "soccer match": "swap positions",
            "book exchange": "swap books",
            "square dance": "swap partners",
        }

        people: List[str] = identity["people"]
        if len(people) == 1:
            people_list = people[0]
        else:
            people_list = ", ".join(people[:-1]) + f" and {people[-1]}"

        initial_desc = "; ".join(
            f"{person} has {obj}" for person, obj in identity["initial_assignments"].items()
        )

        swaps_lines = []
        for idx, (a, b) in enumerate(identity["swaps"], start=1):
            swaps_lines.append(f"{idx}. {a} and {b} {verbs[context_type]}.")

        return templates[context_type].format(
            people_list=people_list,
            initial_desc=initial_desc,
            swaps_desc="\n".join(swaps_lines),
            target=identity["question_person"],
        )

    # ------------------------------------------------------------------ #
    # 内部逻辑
    # ------------------------------------------------------------------ #
    def _generate_people_names(self) -> List[str]:
        count = self.rng.randint(self.min_people, self.max_people)
        if count > len(self.PEOPLE_POOL):
            raise ValueError(f"需要的人数超过内置姓名池容量。{count} > {len(self.PEOPLE_POOL)}")
        return self.PEOPLE_POOL[:count]

    def _select_context_type(self) -> str:
        if self.context_type is not None:
            if self.context_type not in self.OBJECT_POOLS:
                raise ValueError(f"未知的 context_type: {self.context_type}")
            return self.context_type
        return self.rng.choice(self.DEFAULT_CONTEXTS)

    def _build_object_pool(self, context_type: str) -> List[str]:
        pool = list(dict.fromkeys(self.OBJECT_POOLS[context_type]))
        target_size = self.object_pool_size

        if context_type in {"game of catch", "gift exchange"}:
            pool = self._ensure_capacity(pool, target_size, COLOR_LIBRARY)
        elif context_type == "soccer match":
            pool = self._ensure_capacity(pool, target_size, SOCCER_VARIANTS)
        elif context_type == "book exchange":
            pool = self._ensure_capacity(pool, target_size, BOOK_LIBRARY)
        elif context_type == "square dance":
            pool = self._ensure_capacity(pool, target_size, SQUARE_PARTNER_LABELS)

        if len(pool) < target_size:
            pool = self._ensure_capacity(
                pool,
                target_size,
                self._generate_fallback_candidates(context_type),
            )

        self.rng.shuffle(pool)
        return pool[:target_size]

    def _ensure_capacity(
        self,
        base_pool: List[str],
        target_size: int,
        candidates: List[str],
    ) -> List[str]:
        pool = list(base_pool)
        for candidate in candidates:
            if len(pool) >= target_size:
                break
            if candidate not in pool:
                pool.append(candidate)
        return pool

    def _generate_fallback_candidates(self, context_type: str) -> List[str]:
        prefix_map = {
            "game of catch": "color",
            "gift exchange": "gift",
            "soccer match": "position",
            "book exchange": "book",
            "square dance": "partner",
        }
        prefix = prefix_map.get(context_type, "item")
        return [f"{prefix} option {idx}" for idx in range(1, 257)]

    def _generate_valid_swaps(self, people: List[str]) -> List[Tuple[str, str]]:
        if len(people) < 2:
            raise ValueError("至少需要两人才能进行交换。")

        allow_repeated_pair = len(people) == 2
        target_swaps = len(people)

        people_shuffled = people[:]
        self.rng.shuffle(people_shuffled)

        involvement = {person: 0 for person in people}
        swaps: List[Tuple[str, str]] = []

        if allow_repeated_pair:
            a, b = people_shuffled[:2]
            while len(swaps) < target_swaps:
                swaps.append((a, b))
                involvement[a] += 1
                involvement[b] += 1
            return swaps

        # 先保证每个人至少参与一次（构造一个环形交换序列）
        for idx in range(len(people)):
            a = people_shuffled[idx]
            b = people_shuffled[(idx + 1) % len(people)]
            pair = (a, b)
            swaps.append(pair)
            involvement[a] += 1
            involvement[b] += 1

        previous_pair = tuple(sorted(swaps[-1])) if swaps else None

        # 若需要补足交换次数，继续追加随机交换
        while len(swaps) < target_swaps:
            for _ in range(50):
                a, b = self.rng.sample(people, 2)
                current_pair_sorted = tuple(sorted((a, b)))
                if current_pair_sorted != previous_pair:
                    swaps.append((a, b))
                    involvement[a] += 1
                    involvement[b] += 1
                    previous_pair = current_pair_sorted
                    break
            else:
                raise RuntimeError("无法补足随机交换。")

        return swaps


class BbehShuffObjectInstructionGenerator(BaseInstructionGenerator):
    """BBEH Shuffle Object 任务指令生成器。"""

    def __init__(
        self,
        min_people: int = 3,
        max_people: int = 5,
        context_type: Optional[str] = None,
        object_pool_size: int = 10,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.case_builder = ShuffObjectCaseBuilder(
            min_people=min_people,
            max_people=max_people,
            context_type=context_type,
            object_pool_size=object_pool_size,
            seed=seed,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)

