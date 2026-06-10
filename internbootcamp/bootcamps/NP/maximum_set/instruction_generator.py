import random
import time
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

def compute_complement_graph(adj_list):
    nodes = sorted([int(n) for n in adj_list.keys()])
    complement_adj = {node: [] for node in nodes}
    adj_set = {int(node): set(int(n) for n in neighbors) for node, neighbors in adj_list.items()}
    
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]
            if v not in adj_set.get(u, set()):
                complement_adj[u].append(v)
                complement_adj[v].append(u)
    return complement_adj

class MaxIndependentSetSolver:
    def __init__(self, adj_list, timeout=60):
        self.complement_adj_list = {int(k): set(v) for k, v in compute_complement_graph(adj_list).items()}
        self.nodes = sorted(self.complement_adj_list.keys())
        self.timeout = timeout
        self.start_time = None
        self.best_clique = []

    def _get_common_neighbors(self, clique_nodes, candidate):
        common = self.complement_adj_list.get(candidate, set()).copy()
        for node in clique_nodes:
            common.intersection_update(self.complement_adj_list.get(node, set()))
        return common

    def _construct_greedy_clique(self, start_node):
        clique = [start_node]
        candidates = self.complement_adj_list.get(start_node, set()).copy()
        while candidates:
            best_candidate, max_future_candidates = -1, -1
            for candidate in candidates:
                future_candidates = self._get_common_neighbors(clique, candidate)
                if len(future_candidates) > max_future_candidates:
                    max_future_candidates, best_candidate = len(future_candidates), candidate
            if best_candidate != -1:
                clique.append(best_candidate)
                candidates.intersection_update(self.complement_adj_list.get(best_candidate, set()))
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

class NpMaximumSetInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "maximum-set"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        p = self.params
        num_vertices = random.randint(*p["num_vertices"])
        solution_size = min(random.randint(*p["solution_size"]), num_vertices)

        all_vertices = list(range(num_vertices))
        random.shuffle(all_vertices)
        independent_set = sorted(all_vertices[:solution_size])
        other_vertices = all_vertices[solution_size:]

        adj = {str(i): {} for i in range(num_vertices)}

        for i in range(len(other_vertices)):
            for j in range(i + 1, len(other_vertices)):
                if random.random() < p["edge_density_O"]:
                    u, v = other_vertices[i], other_vertices[j]
                    adj[str(u)][str(v)] = 1
                    adj[str(v)][str(u)] = 1
        
        for o_node in other_vertices:
            i_node_to_connect = random.choice(independent_set)
            adj[str(o_node)][str(i_node_to_connect)] = 1
            adj[str(i_node_to_connect)][str(o_node)] = 1
            for i_node in independent_set:
                if i_node != i_node_to_connect and random.random() < p["edge_density_IO"]:
                    adj[str(o_node)][str(i_node)] = 1
                    adj[str(i_node)][str(o_node)] = 1

        # While the generation method predefines an independent set, we solve it
        # on the complement graph to find a potentially larger one, giving a more robust ground truth.
        solver = MaxIndependentSetSolver(adj, timeout=5)
        solution = solver.solve()
        ground_truth = len(solution)

        return {"difficulty": self.difficulty, "question": adj, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/maximum_set/maximum-set.md"
        task_info = extract_markdown_content_NP(md_file)
        
        graph_dict = identity["question"]
        graph_str = "{\n"
        for u in sorted(graph_dict.keys(), key=int):
            neighbors = graph_dict[u]
            neighbor_str = ", ".join([f'"{v}": {w}' for v, w in sorted(neighbors.items(), key=lambda item: int(item[0]))])
            graph_str += f'"{u}": {{{neighbor_str}}},\n'
        graph_str = graph_str.rstrip(",\n") + "\n}"
            
        prompt = get_prompt(self.task_type, task_info, graph_str)
        return prompt

if __name__ == "__main__":
    generator = NpMaximumSetInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
