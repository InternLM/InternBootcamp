import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpSetCoverRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        solution_str = response.split("Answer:")[-1].strip()

        if solution_str == "Impossible":
            return {"format": True, "answer": True, "str": "Impossible"}

        try:
            # Handle list-like strings
            if solution_str.startswith('[') and solution_str.endswith(']'):
                solution_str = solution_str[1:-1]
            
            if not solution_str.strip():
                selected_subsets = []
            else:
                selected_subsets = [int(x.strip()) for x in solution_str.split(',')]
            
            return {"format": True, "answer": True, "str": str(selected_subsets)}

        except (ValueError, IndexError):
            return {"format": True, "answer": False, "str": "Invalid answer format. Should be a list of integers."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward

        U = set(identity["question"]["U"])
        S = identity["question"]["S"]
        
        solution = extracted_output["str"]

        # Case 1: Model claims impossibility
        if solution == "Impossible":
            # Check if it was actually possible
            all_subsets_union = set().union(*[set(s) for s in S.values()])
            if all_subsets_union.issuperset(U):
                answer_reward = -1.5  # Incorrectly claimed impossible
            else:
                answer_reward = 1.0 # Correctly identified impossibility
            return format_reward + answer_reward
            
        # Case 2: Model provides a solution set
        try:
            selected_ids = ast.literal_eval(solution)
            if not isinstance(selected_ids, list): raise ValueError
        except (ValueError, SyntaxError):
            answer_reward = -1.5 # Should have been caught by extractor
            return format_reward + answer_reward
        
        # Validation checks
        covered_elements = set()
        for subset_id in selected_ids:
            if str(subset_id) not in S:
                answer_reward = -1.5 # Invalid subset ID
                return format_reward + answer_reward
            covered_elements.update(S[str(subset_id)])
            
        if not covered_elements.issuperset(U):
            answer_reward = -1.5 # Did not cover all elements
            return format_reward + answer_reward

        # Scoring based on ground truth
        num_selected = len(selected_ids)
        ground_truth = identity.get("ground_truth")
        
        if ground_truth is not None and ground_truth > 0:
            answer_reward = ground_truth / num_selected if num_selected > 0 else 0
        else: # Handle cases with no ground truth or empty solution
             answer_reward = 1.0 if num_selected == 0 and not U else 0

        total_reward = format_reward + answer_reward
        return total_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
