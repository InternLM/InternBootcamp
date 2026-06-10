import random
import time
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class MaxCliqueSolver:
    def __init__(self, adj_list, timeout=60):
        self.adj_list = {int(k): set(int(v) for v in vs) for k, vs in adj_list.items()}
        self.nodes = sorted(self.adj_list.keys())
        self.timeout = timeout
        self.start_time = None
        self.best_clique = []

    def _get_common_neighbors(self, clique_nodes, candidate):
        common = self.adj_list.get(candidate, set()).copy()
        for node in clique_nodes:
            common.intersection_update(self.adj_list.get(node, set()))
        return common

    def _construct_greedy_clique(self, start_node):
        clique = [start_node]
        candidates = self.adj_list.get(start_node, set()).copy()
        while candidates:
            best_candidate, max_future_candidates = -1, -1
            for candidate in candidates:
                future_candidates = self._get_common_neighbors(clique, candidate)
                if len(future_candidates) > max_future_candidates:
                    max_future_candidates, best_candidate = len(future_candidates), candidate
            
            if best_candidate != -1:
                clique.append(best_candidate)
                candidates.intersection_update(self.adj_list.get(best_candidate, set()))
            else: break
        return clique

    def solve(self):
        self.start_time = time.time()
        if not self.nodes: return []
        
        nodes_to_try = self.nodes[:]
        random.shuffle(nodes_to_try)

        for start_node in nodes_to_try:
            if time.time() - self.start_time > self.timeout: break
            clique = self._construct_greedy_clique(start_node)
            if len(clique) > len(self.best_clique):
                self.best_clique = clique
        return self.best_clique


class NpMaximumCliqueProblemInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "maximum-clique-problem"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        p = self.params
        num_vertices = random.randint(*p["num_vertices"])
        clique_size = min(random.randint(*p["clique_size"]), num_vertices)

        all_vertices = list(range(num_vertices))
        random.shuffle(all_vertices)
        clique_nodes = sorted(all_vertices[:clique_size])
        
        adj = {str(i): {} for i in range(num_vertices)}

        # Create the clique
        for i in range(len(clique_nodes)):
            for j in range(i + 1, len(clique_nodes)):
                u, v = clique_nodes[i], clique_nodes[j]
                adj[str(u)][str(v)] = 1
                adj[str(v)][str(u)] = 1
        
        # Add noise (random edges)
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if random.random() < p["noise"]:
                    adj[str(i)][str(j)] = 1
                    adj[str(j)][str(i)] = 1

        solver = MaxCliqueSolver(adj, timeout=5)
        solution = solver.solve()
        ground_truth = len(solution)

        # Convert adj to the final format {str: [str]} for the question
        question_adj = {k: list(v.keys()) for k, v in adj.items()}

        return {"difficulty": self.difficulty, "question": question_adj, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/maximum_clique_problem/maximum-clique-problem.md"
        task_info = extract_markdown_content_NP(md_file)
        
        graph_dict = identity["question"]
        graph_str = "{\n"
        for u in sorted(graph_dict.keys(), key=int):
            neighbors = sorted([int(n) for n in graph_dict[u]])
            graph_str += f'"{u}": {neighbors},\n'
        graph_str = graph_str.rstrip(",\n") + "\n}"
            
        prompt = get_prompt(self.task_type, task_info, graph_str)
        return prompt

if __name__ == "__main__":
    generator = NpMaximumCliqueProblemInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
