import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpMaximumSetRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        answer_part = response.split("Answer:")[-1].strip()

        try:
            # Safely evaluate the string to a Python literal
            node_list = ast.literal_eval(answer_part)
            if not isinstance(node_list, list) or not all(isinstance(i, int) for i in node_list):
                return {"format": True, "answer": False, "str": "Answer must be a list of integers."}
            return {"format": True, "answer": True, "str": str(node_list)}
        except (ValueError, SyntaxError):
            return {"format": True, "answer": False, "str": "Invalid list format in answer."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward
        
        graph = identity["question"]
        
        try:
            independent_set = ast.literal_eval(extracted_output["str"])
        except (ValueError, SyntaxError):
            return format_reward - 1.5

        # --- VALIDATION ---
        # 1. Check if all nodes in the proposed set exist in the graph
        all_graph_nodes = set(graph.keys())
        for node in independent_set:
            if str(node) not in all_graph_nodes:
                return format_reward - 1.5 # Node not in graph

        # 2. Check for independence (no two nodes are adjacent)
        for i in range(len(independent_set)):
            for j in range(i + 1, len(independent_set)):
                u, v = str(independent_set[i]), str(independent_set[j])
                if v in graph.get(u, {}):
                    return format_reward - 1.5 # Nodes are adjacent

        # --- SCORING ---
        size_of_set = len(independent_set)
        ground_truth = identity.get("ground_truth")

        if ground_truth is not None and ground_truth > 0:
            answer_reward = size_of_set / ground_truth
        elif ground_truth == 0:
            answer_reward = 1.0 if size_of_set == 0 else 0.0
        else:
            answer_reward = 0.0

        return format_reward + answer_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
