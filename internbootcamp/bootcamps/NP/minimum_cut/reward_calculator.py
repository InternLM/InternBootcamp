import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpMinimumCutRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        cut_str = response.split("Answer:")[-1].strip()

        try:
            subsets = ast.literal_eval(cut_str)
            if isinstance(subsets, list) and len(subsets) == 2 and \
               isinstance(subsets[0], list) and isinstance(subsets[1], list):
                return {"format": True, "answer": True, "str": str(subsets)}
            else:
                return {"format": True, "answer": False, "str": "Answer should be a list of two lists."}
        except (ValueError, SyntaxError):
            return {"format": True, "answer": False, "str": "Invalid list format in answer."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward

        graph = identity["question"]
        all_nodes = set(int(node) for node in graph.keys())
        n = len(all_nodes)

        try:
            subsets = ast.literal_eval(extracted_output["str"])
            set1, set2 = set(subsets[0]), set(subsets[1])
        except (ValueError, SyntaxError):
            answer_reward = -1.5 # Should be caught by extractor
            return format_reward + answer_reward
            
        # 1. Disjointness
        if not set1.isdisjoint(set2):
            answer_reward = -1.5
            return format_reward + answer_reward

        # 2. Coverage
        if (set1 | set2) != all_nodes:
            answer_reward = -1.5
            return format_reward + answer_reward

        # 3. Balance Constraint
        diff = abs(len(set1) - len(set2))
        is_balanced = (diff == 0) if (n % 2 == 0) else (diff == 1)
        if not is_balanced:
            answer_reward = -1.5
            return format_reward + answer_reward

        # 4. Calculate Cut Weight
        cut_weight = 0
        for u_str, neighbors in graph.items():
            u = int(u_str)
            if u in set1:
                for v_str, weight in neighbors.items():
                    v = int(v_str)
                    if v in set2:
                        cut_weight += weight
        
        # Scoring based on ground truth
        ground_truth = identity.get("ground_truth")
        if ground_truth is not None and ground_truth > 0:
            answer_reward = ground_truth / cut_weight if cut_weight > 0 else 1.0 if ground_truth == 0 else 0
        elif ground_truth == 0:
             answer_reward = 1.0 if cut_weight == 0 else -1.0
        else:
            answer_reward = 0 # No ground truth available

        total_reward = format_reward + answer_reward
        return total_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
