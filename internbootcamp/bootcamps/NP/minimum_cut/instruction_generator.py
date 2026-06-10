import random
from itertools import combinations
from typing import Dict, Any, Optional, List, Tuple, Set

import networkx as nx
from networkx.algorithms.community import kernighan_lin_bisection

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class MinBisectionSolver:
    def __init__(self, graph: nx.Graph, exact_threshold: int = 16, kl_restarts: int = 8):
        self.graph = graph
        self.exact_threshold = exact_threshold
        self.kl_restarts = kl_restarts

    def _cut_weight_of_partition(self, set1: Set[int], set2: Set[int]) -> int:
        w = 0
        for u in set1:
            for v in set2:
                if self.graph.has_edge(u, v):
                    w += self.graph[u][v].get('weight', 1)
        return int(w)

    def solve(self) -> Tuple[List[int], List[int], int]:
        n = self.graph.number_of_nodes()
        nodes = list(self.graph.nodes())
        if n < 2:
            return [], [], 0

        if n <= self.exact_threshold:
            best_w = float('inf')
            best_part = None
            sizes = [n // 2] if n % 2 == 0 else [n // 2] # n//2+1 is redundant due to symmetry
            
            anchor = nodes[0]
            rest = nodes[1:]
            for k in sizes:
                need = k - 1
                if not (0 <= need <= len(rest)): continue
                for combo in combinations(rest, need):
                    S = set([anchor]) | set(combo)
                    T = set(nodes) - S
                    w = self._cut_weight_of_partition(S, T)
                    if w < best_w:
                        best_w, best_part = w, (sorted(list(S)), sorted(list(T)))
            return best_part[0], best_part[1], int(best_w) if best_part else ([], [], 0)

        else: # KL Heuristic for larger graphs
            G_kl = self.graph.copy()
            dummy = None
            if n % 2 == 1:
                dummy = f"__DUMMY__{n}"
                G_kl.add_node(dummy)
            
            best_w = float('inf')
            best_part = None
            for _ in range(self.kl_restarts):
                nodes_kl = list(G_kl.nodes())
                random.shuffle(nodes_kl)
                half = len(nodes_kl) // 2
                A_init, B_init = set(nodes_kl[:half]), set(nodes_kl[half:])
                try:
                    A, B = kernighan_lin_bisection(G_kl, partition=(A_init, B_init), weight='weight')
                except (nx.NetworkXError, ValueError): # Handle disconnected or other KL errors
                    continue

                if dummy:
                    A.discard(dummy)
                    B.discard(dummy)
                
                w = self._cut_weight_of_partition(set(A), set(B))
                if w < best_w:
                    best_w, best_part = w, (sorted(list(A)), sorted(list(B)))
            
            return best_part[0], best_part[1], int(best_w) if best_part else ([], [], 0)


class NpMinimumCutInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "minimum-cut"
        self.params = kwargs

    def _generate_graph(self) -> nx.Graph:
        num_nodes = self.params["num_nodes"]
        G = nx.Graph()
        nodes = list(range(num_nodes))
        G.add_nodes_from(nodes)
        
        half = num_nodes // 2
        set_A, set_B = nodes[:half], nodes[half:]

        # Intra-community edges
        for u, v in combinations(set_A, 2):
            if random.random() < self.params["intra_density"]:
                G.add_edge(u, v, weight=random.randint(5, 10))
        for u, v in combinations(set_B, 2):
            if random.random() < self.params["intra_density"]:
                G.add_edge(u, v, weight=random.randint(5, 10))
        
        # Inter-community edges
        for _ in range(self.params["inter_edges"]):
            u, v = random.choice(set_A), random.choice(set_B)
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=random.randint(1, 4))
        
        # Ensure connectivity
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                u, v = random.choice(list(components[i])), random.choice(list(components[i+1]))
                if not G.has_edge(u, v):
                    G.add_edge(u, v, weight=random.randint(1, 3))
        
        return G

    def _graph_to_dict(self, G: nx.Graph) -> Dict:
        adj_dict = {}
        for u in sorted(G.nodes()):
            adj_dict[str(u)] = {str(v): data['weight'] for v, data in G[u].items()}
        return adj_dict

    def case_generator(self) -> Dict[str, Any]:
        graph_nx = self._generate_graph()
        
        solver = MinBisectionSolver(graph_nx)
        _, _, ground_truth = solver.solve()
        
        question_dict = self._graph_to_dict(graph_nx)

        identity = {
            "difficulty": self.difficulty,
            "question": question_dict,
            "ground_truth": ground_truth
        }
        return identity

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/minimum_cut/minimum-cut.md"
        task_info = extract_markdown_content_NP(md_file)
        
        graph_dict = identity["question"]
        graph_str = ""
        for u in sorted(graph_dict.keys(), key=int):
            neighbors = graph_dict[u]
            # Format neighbors nicely
            neighbor_str = ", ".join([f"{v}: {w}" for v, w in sorted(neighbors.items(), key=lambda item: int(item[0]))])
            graph_str += f"{u}: {{{neighbor_str}}}\n"
            
        prompt = get_prompt(self.task_type, task_info, graph_str.strip())
        return prompt

if __name__ == "__main__":
    generator = NpMinimumCutInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
