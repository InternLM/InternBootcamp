import sys
from pathlib import Path
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
import re

class NpGcpDRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" in response:
            color_str = response.split("Answer:")[-1].strip()
        else:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}

        color_str = color_str.strip().replace("'", "").replace('"', '')
        pattern = r'[{\[\(]([^)}\]]*)[}\])]'
        match = re.search(pattern, color_str)
        if match:
            color_str = match.group(1)
        
        try:
            colors = [int(x.strip()) for x in color_str.split(',') if x.strip() != '']
        except:
            return {"format": True, "answer": False, "str": "coloring must be a list of integers"}

        if not colors:
            return {"format": True, "answer": False, "str": "coloring cannot be empty"}

        return {"format": True, "answer": True, "str": str(colors)}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        if not extracted_output.get('format', False):
            format_reward = -1.0
        else:
            format_reward = 1.0

        if not extracted_output.get('answer', False):
            answer_reward = -1.5
        else:
            graph = identity.get("question", {})
            num_vertices = len(graph)
            
            try:
                colors_str = extracted_output['str'].strip('[]')
                colors = [int(x.strip()) for x in colors_str.split(',') if x.strip()]
            except (ValueError, IndexError):
                answer_reward = -1.5 # Should have been caught by extract_output, but as a safeguard.
                return format_reward + answer_reward

            # 1. Check number of vertices
            if len(colors) != num_vertices:
                answer_reward = -1.5
                return format_reward + answer_reward
            
            # 2. Check for invalid colors (e.g., <= 0)
            if any(c <= 0 for c in colors):
                answer_reward = -1.5
                return format_reward + answer_reward

            # 3. Check for valid coloring (adjacency check)
            is_valid = True
            for node_str, neighbors in graph.items():
                node = int(node_str)
                node_color = colors[node]
                for neighbor_str in neighbors:
                    neighbor = int(neighbor_str)
                    if node_color == colors[neighbor]:
                        is_valid = False
                        break
                if not is_valid:
                    break
            
            if not is_valid:
                answer_reward = -1.5
            else:
                num_used_colors = len(set(colors))
                ground_truth = identity.get("ground_truth", num_vertices)
                if ground_truth > 0 and num_used_colors > 0:
                    answer_reward = ground_truth / num_used_colors
                else:
                    answer_reward = 0

        total_reward = format_reward + answer_reward
        return total_reward

    @classmethod
    def _verify_correction(cls, extracted_output: dict, identity: dict) -> float:
        score = cls._calculate_score(extracted_output, identity)
        return score
