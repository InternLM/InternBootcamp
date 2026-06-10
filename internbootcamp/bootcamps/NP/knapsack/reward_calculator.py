import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpKnapsackRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        answer_part = response.split("Answer:")[-1].strip()

        try:
            item_list = ast.literal_eval(answer_part)
            if not isinstance(item_list, list) or not all(isinstance(i, int) for i in item_list):
                return {"format": True, "answer": False, "str": "Answer must be a list of integers."}
            return {"format": True, "answer": True, "str": str(item_list)}
        except (ValueError, SyntaxError):
            return {"format": True, "answer": False, "str": "Invalid list format in answer."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward
        
        problem_data = identity["question"]
        capacity = problem_data["capacity"]
        items = problem_data["items"]

        try:
            chosen_items = ast.literal_eval(extracted_output["str"])
        except (ValueError, SyntaxError):
            return format_reward - 1.5

        # --- VALIDATION ---
        # 1. Check for duplicates
        if len(chosen_items) != len(set(chosen_items)):
            return format_reward - 1.5

        total_weight = 0
        total_value = 0
        for item_id in chosen_items:
            item_key = str(item_id)
            if item_key not in items:
                return format_reward - 1.5 # Item does not exist
            
            total_weight += items[item_key]["weight"]
            total_value += items[item_key]["value"]

        # 2. Check capacity constraint
        if total_weight > capacity:
            return format_reward - 1.5

        # --- SCORING ---
        ground_truth = identity.get("ground_truth")
        if ground_truth is not None and ground_truth > 0:
            answer_reward = total_value / ground_truth
        elif ground_truth == 0:
            answer_reward = 1.0 if total_value == 0 else 0.0
        else:
            answer_reward = 0.0

        return format_reward + answer_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
