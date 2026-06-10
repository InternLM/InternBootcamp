import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from collections import defaultdict

class NpMaximumCliqueProblemRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        answer_part = response.split("Answer:")[-1].strip()

        try:
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
            clique = ast.literal_eval(extracted_output["str"])
        except (ValueError, SyntaxError):
            return format_reward - 1.5

        # --- VALIDATION ---
        # 1. Normalize graph to {int: set(int)}
        adj = defaultdict(set)
        all_nodes = set()
        for u_str, neighbors in graph.items():
            u = int(u_str)
            all_nodes.add(u)
            for v_str in neighbors:
                v = int(v_str)
                adj[u].add(v)
                adj[v].add(u)
                all_nodes.add(v)

        # 2. Check if all nodes in clique exist
        for node in clique:
            if node not in all_nodes:
                return format_reward - 1.5 # Node not in graph
        
        # 3. Check if it's a clique
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                u, v = clique[i], clique[j]
                if v not in adj.get(u, set()):
                    return format_reward - 1.5 # Not fully connected

        # --- SCORING ---
        size_of_clique = len(clique)
        ground_truth = identity.get("ground_truth")

        if ground_truth is not None and ground_truth > 0:
            answer_reward = size_of_clique / ground_truth
        elif ground_truth == 0:
            answer_reward = 1.0 if size_of_clique == 0 else 0.0
        else:
            answer_reward = 0.0

        return format_reward + answer_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
