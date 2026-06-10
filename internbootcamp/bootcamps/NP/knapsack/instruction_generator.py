import random
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class KnapsackSolver:
    def __init__(self, items, capacity):
        self.items = sorted(items, key=lambda x: x[0])
        self.capacity = int(capacity)
        self.num_items = len(self.items)

    def solve(self):
        dp = [[0 for _ in range(self.capacity + 1)] for _ in range(self.num_items + 1)]

        for i in range(1, self.num_items + 1):
            _item_id, item_weight, item_value = self.items[i - 1]
            for w in range(self.capacity + 1):
                if item_weight <= w:
                    dp[i][w] = max(item_value + dp[i - 1][w - item_weight], dp[i - 1][w])
                else:
                    dp[i][w] = dp[i - 1][w]
        
        max_value = dp[self.num_items][self.capacity]
        selected_ids, w = [], self.capacity
        for i in range(self.num_items, 0, -1):
            if w > 0 and dp[i][w] != dp[i - 1][w]:
                item_id, item_weight, _ = self.items[i - 1]
                selected_ids.append(item_id)
                w -= item_weight
        
        return sorted(selected_ids), max_value

class NpKnapsackInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "knapsack"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        p = self.params
        num_items = random.randint(*p["num_items"])

        items_dict = {}
        items_list = []
        total_weight = 0
        for i in range(num_items):
            weight = random.randint(*p["weight_range"])
            value = int(weight * random.uniform(*p["value_ratio"]))
            items_dict[str(i)] = {"weight": weight, "value": value}
            items_list.append((i, weight, value))
            total_weight += weight
        
        capacity = int(total_weight * p["capacity_factor"])
        
        solver = KnapsackSolver(items_list, capacity)
        _, ground_truth = solver.solve()
        
        question = {"capacity": capacity, "items": items_dict}
        return {"difficulty": self.difficulty, "question": question, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/knapsack/knapsack.md"
        task_info = extract_markdown_content_NP(md_file)
        
        q = identity["question"]
        question_str = f'{{\n  "capacity": {q["capacity"]},\n  "items": {{\n'
        items_str = ",\n".join([f'    "{k}": {v}' for k, v in q["items"].items()])
        question_str += items_str.replace("'", '"') + "\n  }\n}"
            
        prompt = get_prompt(self.task_type, task_info, question_str)
        return prompt

if __name__ == "__main__":
    generator = NpKnapsackInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
