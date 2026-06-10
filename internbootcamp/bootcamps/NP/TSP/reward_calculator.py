import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpTspRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        path_str = response.split("Answer:")[-1].strip()

        try:
            path = ast.literal_eval(path_str)
            if not isinstance(path, list) or not all(isinstance(i, int) for i in path):
                return {"format": True, "answer": False, "str": "Answer must be a list of integers."}
            return {"format": True, "answer": True, "str": str(path)}
        except (ValueError, SyntaxError):
            return {"format": True, "answer": False, "str": "Invalid list format in answer."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward
        
        graph = identity["question"]
        num_cities = len(graph)

        try:
            path = ast.literal_eval(extracted_output["str"])
        except (ValueError, SyntaxError):
            return format_reward - 1.5

        # --- VALIDATION ---
        if not path or path[0] != path[-1]:
            return format_reward - 1.5  # Not a cycle
        
        if len(path) != num_cities + 1 or len(set(path[:-1])) != num_cities:
            return format_reward - 1.5 # Doesn't visit all cities exactly once

        total_distance = 0
        for i in range(len(path) - 1):
            u, v = str(path[i]), str(path[i+1])
            try:
                total_distance += graph[u][v]
            except KeyError:
                return format_reward - 1.5 # Invalid edge

        # --- SCORING ---
        ground_truth = identity.get("ground_truth")
        if ground_truth is not None and ground_truth > 0:
            # For TSP, lower is better, so the ratio is inverted.
            answer_reward = ground_truth / total_distance if total_distance > 0 else 1.0
        elif ground_truth == 0:
            answer_reward = 1.0 if total_distance == 0 else 0.0
        else:
            answer_reward = 0.0

        return format_reward + answer_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
