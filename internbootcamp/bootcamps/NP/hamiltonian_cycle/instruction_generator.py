import random
import time
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class LongestCycleSolver:
    def __init__(self, adj_list, timeout):
        self.adj_list = {int(k): v for k, v in adj_list.items()}
        self.nodes = list(self.adj_list.keys())
        self.timeout = timeout
        self.start_time = None
        self.best_cycle = []

    def _get_unvisited_neighbors(self, node, current_path_set):
        return [n for n in self.adj_list.get(node, []) if n not in current_path_set]

    def _greedy_path_construction(self, start_node):
        path, path_set = [start_node], {start_node}
        current_node = start_node
        while True:
            unvisited_neighbors = self._get_unvisited_neighbors(current_node, path_set)
            if not unvisited_neighbors: break
            next_node = min(unvisited_neighbors, key=lambda n: len(self._get_unvisited_neighbors(n, path_set)))
            path.append(next_node)
            path_set.add(next_node)
            current_node = next_node
        return path

    def _close_path_to_cycle(self, path):
        if len(path) < 3: return []
        end_node_neighbors = self.adj_list.get(path[-1], [])
        for i, node in enumerate(path):
            if node in end_node_neighbors:
                return path[i:] + [node]
        return []

    def _improve_cycle(self, cycle):
        current_cycle = list(cycle)
        while True:
            cycle_set = set(current_cycle)
            unvisited = [n for n in self.nodes if n not in cycle_set]
            if not unvisited: break
            
            inserted = False
            random.shuffle(unvisited)
            for node_to_insert in unvisited:
                neighbors_of_insert = set(self.adj_list.get(node_to_insert, []))
                for i in range(len(current_cycle) - 1):
                    u, v = current_cycle[i], current_cycle[i+1]
                    if u in neighbors_of_insert and v in neighbors_of_insert:
                        current_cycle.insert(i + 1, node_to_insert)
                        inserted = True
                        break
                if inserted: break
            if not inserted: break
        return current_cycle

    def solve(self):
        self.start_time = time.time()
        if not self.nodes: return None
        
        while time.time() - self.start_time < self.timeout:
            start_node = random.choice(self.nodes)
            path = self._greedy_path_construction(start_node)
            cycle = self._close_path_to_cycle(path)
            if cycle:
                cycle = self._improve_cycle(cycle)
            if len(cycle) > len(self.best_cycle):
                self.best_cycle = cycle
        return self.best_cycle if self.best_cycle else None


class NpHamiltonianCycleInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "hamiltonian-cycle"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        num_vertices = random.randint(*self.params["num_vertices"])
        nodes = list(range(num_vertices))
        random.shuffle(nodes)
        
        adj = {str(i): {} for i in range(num_vertices)}
        for i in range(len(nodes)):
            u, v = nodes[i], nodes[(i + 1) % num_vertices]
            adj[str(u)][str(v)] = 1
            adj[str(v)][str(u)] = 1
            
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if str(j) not in adj[str(i)] and random.random() < self.params["edge_density"]:
                    adj[str(i)][str(j)] = 1
                    adj[str(j)][str(i)] = 1

        question_adj = {k: [int(n) for n in v.keys()] for k,v in adj.items()}
        
        # Use the solver to find the longest cycle, which should be the Hamiltonian cycle
        solver = LongestCycleSolver(question_adj, timeout=5)
        solution = solver.solve()
        ground_truth = len(solution) -1 if solution else 0 # Length of cycle is number of unique nodes

        return {"difficulty": self.difficulty, "question": question_adj, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/hamiltonian_cycle/hamiltonian-cycle.md"
        task_info = extract_markdown_content_NP(md_file)
        
        graph_dict = identity["question"]
        graph_str = ""
        for u in sorted(graph_dict.keys(), key=int):
            neighbors = sorted(graph_dict[u])
            graph_str += f"{u}: {neighbors}\n"
            
        prompt = get_prompt(self.task_type, task_info, graph_str.strip())
        return prompt

if __name__ == "__main__":
    generator = NpHamiltonianCycleInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
