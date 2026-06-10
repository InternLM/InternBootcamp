from __future__ import annotations

import random
from copy import deepcopy
from typing import Any, Dict, List, Optional

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class ObjectPropertiesCaseBuilder:
    """负责生成 BBEH Object Properties 任务中的案例与题面。"""

    RELATIVES = [
        "mom",
        "dad",
        "sister",
        "brother",
        "cousin",
        "aunt",
        "uncle",
        "friend",
        "fiance",
        "teacher",
        "neighbor",
    ]

    def __init__(
        self,
        min_items: int = 25,
        max_items: int = 40,
        min_steps: int = 4,
        max_steps: int = 6,
        rng: Optional[random.Random] = None,
    ):
        if min_items <= 0 or max_items < min_items:
            raise ValueError("min_items 与 max_items 参数非法")
        if min_steps <= 0 or max_steps < min_steps:
            raise ValueError("min_steps 与 max_steps 参数非法")

        self.min_items = min_items
        self.max_items = max_items
        self.min_steps = min_steps
        self.max_steps = max_steps
        self.rng = rng or random.Random()

        self.sizes: List[str] = [
            "extra-extra-small",
            "extra-small",
            "small",
            "medium",
            "large",
            "extra-large",
            "extra-extra-large",
        ]
        self.origins: List[str] = [
            "Spanish",
            "Turkish",
            "French",
            "Russian",
            "British",
            "Mexican",
            "Afghan",
            "Portuguese",
            "Canadian",
            "Japanese",
            "Iranian",
            "Italian",
            "German",
            "Chinese",
            "Polish",
            "Brazilian",
        ]
        self.materials: List[str] = [
            "plastic",
            "steel",
            "glass",
            "ceramic",
            "concrete",
        ]
        self.smells: List[str] = [
            "vinegar",
            "pine needles",
            "freshly cut grass",
            "coffee",
            "rose",
            "citrus fruits",
            "lavender",
            "burning wood",
            "garlic",
            "gasoline",
            "coconut",
            "popcorn",
            "wet dog",
            "leather",
            "baking bread",
            "chocolate",
            "vanilla",
        ]
        self.names: List[str] = [
            "calculator",
            "hat",
            "jar",
            "plier",
            "sunglasses",
            "drill",
            "canvas",
            "ring",
            "screwdriver",
            "camera",
            "bird",
            "ruler",
            "hammer",
            "umbrella",
            "shoe",
            "cup",
            "fork",
            "key",
            "house",
            "brush",
            "book",
            "candle",
            "bicycle",
            "vase",
            "clock",
            "sofa",
            "trash can",
            "marker",
            "bottle",
            "banana",
            "flower pot",
            "table",
            "wallet",
            "box",
            "chair",
            "ring",
            "earring",
            "pen",
            "stapler",
            "saw",
            "shoe",
            "scissors",
            "ladder",
            "shelf",
        ]
        self.colors: List[str] = [
            "beige",
            "black",
            "blue",
            "brown",
            "crimson",
            "cyan",
            "gold",
            "gray",
            "green",
            "indigo",
            "ivory",
            "khaki",
            "magenta",
            "maroon",
            "orange",
            "pink",
            "purple",
            "red",
            "silver",
            "teal",
            "turquoise",
            "violet",
            "white",
            "yellow",
        ]

        self.available_operations = [
            self._duplicate_by_color,
            self._duplicate_by_smell,
            self._replace_size_with_variants,
            self._change_material_preferences,
            self._replace_origin_with_pairs,
            self._lose_one_item,
        ]

    def _choice(self, seq: List[Any]) -> Any:
        if not seq:
            raise ValueError("待选序列为空，无法随机选择")
        return self.rng.choice(seq)

    # ------------------------------------------------------------------ #
    # 公共接口
    # ------------------------------------------------------------------ #
    def generate_case(self) -> Dict[str, Any]:
        case = self._generate_initial_case()
        num_steps = self.rng.randint(self.min_steps, self.max_steps)

        for _ in range(num_steps):
            operation = self.rng.choice(self.available_operations)
            updated = operation(case)
            # 某些操作在条件不足时会返回 None，表示跳过
            if updated is not None:
                case = updated

        question = self._generate_question(case["final_objects"])
        answer = self._compute_answer(case["final_objects"], question)
        question_text = self._format_question_text(question)

        case.update(
            {
                "question": question,
                "question_text": question_text,
                "answer": answer,
            }
        )
        return case

    @staticmethod
    def construct_prompt(identity: Dict[str, Any]) -> str:
        initial_objects: List[Dict[str, str]] = identity.get("initial_objects", [])
        color_blocks: List[Dict[str, Any]] = identity.get("color_blocks", [])
        steps: List[Dict[str, Any]] = identity.get("steps", [])
        question_text: str = identity.get("question_text", "")

        prompt_lines: List[str] = []
        prompt_lines.append(
            f"I had a collection of {len(initial_objects)} weird items that went through a few changes. Initially,"
        )

        for idx, obj in enumerate(initial_objects, start=1):
            prompt_lines.append(
                f"{idx}. an {obj['size']} {obj['origin']} {obj['name']} made of {obj['material']} with a smell of {obj['smell']}."
            )

        if color_blocks:
            color_desc = ["The color of the items was respectively as follows:"]
            running = 0
            for block in color_blocks:
                running += block["count"]
                prefix = "the first" if running == block["count"] else "the next"
                color_word = "was" if block["count"] == 1 else "were"
                color_desc.append(f"{prefix} {block['count']} {color_word} {block['color']}")
            prompt_lines.append(" ".join(color_desc) + ".")

        for step in steps:
            prompt_lines.append(step["description"])

        prompt_lines.append(
            f"In my current collection, how many items have the following attributes: {question_text}? "
            "If the exact number cannot be computed, the answer must be 'unknown'."
        )
        prompt_lines.append("Please put your final answer within <answer></answer> tags(e.g. <answer>your_answer</answer>).")
        return "\n".join(prompt_lines)

    # ------------------------------------------------------------------ #
    # 初始案例构建
    # ------------------------------------------------------------------ #
    def _generate_initial_case(self) -> Dict[str, Any]:
        n_items = self.rng.randint(self.min_items, self.max_items)
        color_blocks = self._generate_color_blocks(n_items)

        objects: List[Dict[str, str]] = []
        block_idx = 0
        block_count = 0

        for _ in range(n_items):
            if block_count >= color_blocks[block_idx]["count"]:
                block_idx += 1
                block_count = 0

            obj = {
                "size": self.rng.choice(self.sizes),
                "origin": self.rng.choice(self.origins),
                "material": self.rng.choice(self.materials),
                "smell": self.rng.choice(self.smells),
                "name": self.rng.choice(self.names),
                "color": color_blocks[block_idx]["color"],
            }
            objects.append(obj)
            block_count += 1

        return {
            "initial_objects": deepcopy(objects),
            "final_objects": objects,
            "color_blocks": color_blocks,
            "steps": [],
        }

    def _generate_color_blocks(self, total: int) -> List[Dict[str, Any]]:
        remaining = total
        blocks: List[Dict[str, Any]] = []
        while remaining > 0:
            color = self.rng.choice(self.colors)
            count = self.rng.randint(1, min(5, remaining))
            blocks.append({"color": color, "count": count})
            remaining -= count
        return blocks

    def _format_attribute_counts(self, objects: List[Dict[str, str]], attr: str) -> str:
        counter: Dict[str, int] = {}
        for obj in objects:
            value = obj.get(attr)
            if value is None:
                continue
            counter[value] = counter.get(value, 0) + 1
        if not counter:
            return "0 item(s)"

        sorted_counts = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        parts = [f"{count} {value} item(s)" for value, count in sorted_counts]
        if len(parts) == 1:
            return parts[0]
        return ", ".join(parts[:-1]) + f", and {parts[-1]}"

    # ------------------------------------------------------------------ #
    # 操作定义
    # ------------------------------------------------------------------ #
    def _duplicate_by_color(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        colors = {obj["color"] for obj in objects}
        if not colors:
            return None

        target_color = self.rng.choice(list(colors))
        duplicate_color = self._choice([c for c in self.colors if c != target_color])
        duplicate_origin = self.rng.choice(self.origins)
        duplicate_size = self.rng.choice(self.sizes)
        duplicate_smell = self.rng.choice(self.smells)
        duplicate_material = self.rng.choice(self.materials)
        role = self.rng.choice(self.RELATIVES)

        new_objects: List[Dict[str, str]] = []
        created = 0
        for obj in objects:
            new_objects.append(obj)
            if obj["color"] == target_color:
                clone = deepcopy(obj)
                clone.update(
                    {
                        "color": duplicate_color,
                        "origin": duplicate_origin,
                        "size": duplicate_size,
                        "smell": duplicate_smell,
                        "material": duplicate_material,
                    }
                )
                new_objects.append(clone)
                created += 1

        if created == 0:
            return None

        case = deepcopy(case)
        case["final_objects"] = new_objects
        summary = self._format_attribute_counts(new_objects, "smell")
        case["steps"].append(
            {
                "type": "duplicate_color",
                "description": (
                    f"Then, for any item of color {target_color} in my collection, my {role} gave me another one "
                    f"of the same item, but with a {duplicate_color} color, {duplicate_origin} origin, "
                    f"{duplicate_size} size, {duplicate_smell} smell, and made of {duplicate_material}. "
                    f"After this, my new collection had: {summary}."
                ),
            }
        )
        return case

    def _duplicate_by_smell(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        smells = {obj["smell"] for obj in objects}
        if not smells:
            return None

        selected_smells = self.rng.sample(list(smells), min(2, len(smells)))
        new_smell = self._choice([s for s in self.smells if s not in selected_smells])
        role = self.rng.choice(self.RELATIVES)

        new_objects: List[Dict[str, str]] = []
        created = 0
        for obj in objects:
            new_objects.append(obj)
            if obj["smell"] in selected_smells:
                clone = deepcopy(obj)
                clone["smell"] = new_smell
                new_objects.append(clone)
                created += 1

        if created == 0:
            return None

        case = deepcopy(case)
        case["final_objects"] = new_objects
        summary = self._format_attribute_counts(new_objects, "smell")
        smell_phrase = ", ".join(selected_smells)
        case["steps"].append(
            {
                "type": "duplicate_smell",
                "description": (
                    f"Then, for any item with a smell of {smell_phrase} in my new collection, my {role} gifted me "
                    f"another one of that item with the same properties but with {new_smell} smell. "
                    f"After this, my new collection had: {summary}."
                ),
            }
        )
        return case

    def _replace_size_with_variants(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        sizes = {obj["size"] for obj in objects}
        if not sizes:
            return None

        target_size = self.rng.choice(list(sizes))
        replacement_size = self._choice([s for s in self.sizes if s != target_size])
        replacement_color = self.rng.choice(self.colors)
        role = self.rng.choice(self.RELATIVES)

        new_objects: List[Dict[str, str]] = []
        replaced = 0
        for obj in objects:
            if obj["size"] == target_size:
                size_clone = deepcopy(obj)
                size_clone["size"] = replacement_size

                color_clone = deepcopy(obj)
                color_clone["color"] = replacement_color

                new_objects.extend([size_clone, color_clone])
                replaced += 1
            else:
                new_objects.append(obj)

        if replaced == 0:
            return None

        case = deepcopy(case)
        case["final_objects"] = new_objects
        summary = self._format_attribute_counts(new_objects, "size")
        case["steps"].append(
            {
                "type": "replace_size",
                "description": (
                    f"Then, my {role} replaced any item of size {target_size} in my new collection with an exact copy "
                    f"but with {replacement_size} size and another exact copy but with color {replacement_color}. "
                    f"After this, my new collection had: {summary}."
                ),
            }
        )
        return case

    def _change_material_preferences(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        materials = {obj["material"] for obj in objects}
        if not materials:
            return None

        target_material = self.rng.choice(list(materials))
        new_color = self.rng.choice(self.colors)
        new_smell = self.rng.choice(self.smells)
        role = self.rng.choice(self.RELATIVES)

        new_objects = deepcopy(objects)
        changed = 0
        for obj in new_objects:
            if obj["material"] == target_material:
                obj["color"] = new_color
                obj["smell"] = new_smell
                changed += 1

        if changed == 0:
            return None

        case = deepcopy(case)
        case["final_objects"] = new_objects
        summary = self._format_attribute_counts(new_objects, "color")
        case["steps"].append(
            {
                "type": "change_material",
                "description": (
                    f"Then, for any item made of {target_material} in my new collection, my {role} changed their color "
                    f"to {new_color} and their smell to {new_smell}. After this, my new collection had: {summary}."
                ),
            }
        )
        return case

    def _replace_origin_with_pairs(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        origins = {obj["origin"] for obj in objects}
        if not origins:
            return None

        target_origin = self.rng.choice(list(origins))
        replacement_origins = self.rng.sample(
            [o for o in self.origins if o != target_origin], k=2
        )
        role = self.rng.choice(self.RELATIVES)

        new_objects: List[Dict[str, str]] = []
        replaced = 0
        for obj in objects:
            if obj["origin"] == target_origin:
                clone_a = deepcopy(obj)
                clone_a["origin"] = replacement_origins[0]
                clone_b = deepcopy(obj)
                clone_b["origin"] = replacement_origins[1]
                new_objects.extend([clone_a, clone_b])
                replaced += 1
            else:
                new_objects.append(obj)

        if replaced == 0:
            return None

        case = deepcopy(case)
        case["final_objects"] = new_objects
        summary = self._format_attribute_counts(new_objects, "origin")
        case["steps"].append(
            {
                "type": "replace_origin",
                "description": (
                    f"Then, my {role} threw away any {target_origin} item in my new collection, but gave me two of "
                    f"the same item, one {replacement_origins[0]} and one {replacement_origins[1]} (all other "
                    f"properties the same). After this, my new collection had: {summary}."
                ),
            }
        )
        return case

    def _lose_one_item(self, case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        objects = case["final_objects"]
        if not objects:
            return None

        attr = self.rng.choice(["size", "color", "smell", "origin", "material"])
        candidates = [obj for obj in objects if obj.get(attr)]
        if not candidates:
            return None

        lost_item = self.rng.choice(candidates)
        target_value = lost_item[attr]

        new_objects = deepcopy(objects)
        for idx, obj in enumerate(new_objects):
            if obj[attr] == target_value:
                new_objects.pop(idx)
                break

        case = deepcopy(case)
        case["final_objects"] = new_objects
        plural = "item" if attr == "size" else "items"
        case["steps"].append(
            {
                "type": "lose_one",
                "description": (
                    f"Then, I lost one of the {target_value} {plural} in my collection."
                ),
            }
        )
        return case

    # ------------------------------------------------------------------ #
    # 问题与答案
    # ------------------------------------------------------------------ #
    def _generate_question(self, objects: List[Dict[str, str]]) -> Dict[str, Any]:
        if not objects:
            raise ValueError("final_objects 为空，无法生成问题")

        mode = self.rng.choice(["neither", "either"])
        attributes = ["color", "size", "material", "smell", "origin"]
        num_conditions = self.rng.randint(3, len(attributes))
        selected_attrs = self.rng.sample(attributes, num_conditions)

        conditions = []
        for attr in selected_attrs:
            attr_values = sorted({obj[attr] for obj in objects})
            if not attr_values:
                continue
            if mode == "neither":
                values = self.rng.sample(
                    attr_values, k=min(len(attr_values), self.rng.randint(1, 2))
                )
                conditions.append({"attr": attr, "values": values, "negate": True})
            else:
                values = self.rng.sample(
                    attr_values, k=min(len(attr_values), self.rng.randint(1, 2))
                )
                conditions.append({"attr": attr, "values": values, "negate": False})

        return {"mode": mode, "conditions": conditions}

    def _format_question_text(self, question: Dict[str, Any]) -> str:
        mode = question.get("mode", "neither")
        conditions = question.get("conditions", [])

        def join_values(vals: List[str], conj: str) -> str:
            if len(vals) == 1:
                return vals[0]
            if len(vals) == 2:
                return f"{vals[0]} {conj} {vals[1]}"
            return ", ".join(vals[:-1]) + f", {conj} {vals[-1]}"

        if mode == "either" and conditions:
            parts: List[str] = []
            for cond in conditions:
                values = cond.get("values", [])
                if not values:
                    continue
                value_str = join_values(values, "or")
                parts.append(f"{cond['attr']} is {value_str}")
            if parts:
                return "either " + ", or ".join(parts)
            return "either (no valid attributes)"

        parts = []
        for cond in conditions:
            values = cond.get("values", [])
            if not values:
                continue
            value_str = join_values(values, "nor")
            parts.append(f"{cond['attr']} is not {value_str}")
        return ", ".join(parts) if parts else "no specific constraints"

    def _compute_answer(self, objects: List[Dict[str, str]], question: Dict[str, Any]) -> int:
        mode = question.get("mode", "neither")
        conditions = question.get("conditions", [])
        if not objects:
            return 0
        if not conditions:
            return len(objects) if mode != "either" else 0

        def matches_either(obj: Dict[str, str]) -> bool:
            for cond in conditions:
                values = cond.get("values", [])
                attr_name = cond.get("attr")
                if attr_name is None:
                    continue
                attr_value = obj.get(attr_name)
                if cond.get("negate", False):
                    if attr_value not in values:
                        return True
                else:
                    if attr_value in values:
                        return True
            return False

        def matches_neither(obj: Dict[str, str]) -> bool:
            for cond in conditions:
                values = cond.get("values", [])
                attr_name = cond.get("attr")
                if attr_name is None:
                    continue
                attr_value = obj.get(attr_name)
                if cond.get("negate", True):
                    if attr_value in values:
                        return False
                else:
                    if attr_value not in values:
                        return False
            return True

        matcher = matches_either if mode == "either" else matches_neither
        return sum(1 for obj in objects if matcher(obj))


class BbehObjectPropertiesInstructionGenerator(BaseInstructionGenerator):
    """BBEH Object Properties 任务的指令生成器。"""

    def __init__(
        self,
        min_items: int = 25,
        max_items: int = 40,
        min_steps: int = 4,
        max_steps: int = 6,
        seed: Optional[int] = None,
    ):
        super().__init__()
        rng = random.Random(seed) if seed is not None else None
        self.case_builder = ObjectPropertiesCaseBuilder(
            min_items=min_items,
            max_items=max_items,
            min_steps=min_steps,
            max_steps=max_steps,
            rng=rng,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity) 

