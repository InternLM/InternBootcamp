from typing import Dict, Any, Optional, List, Tuple
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt
import random
import time
from collections import defaultdict

class GCPSolver:
    """
    A solver for the Graph Coloring Problem (GCP-D) using a powerful hybrid
    heuristic approach:
    1. DSatur algorithm for a high-quality initial coloring.
    2. Tabu Search to iteratively try and reduce the number of colors used.
    """
    def __init__(self, adj_list, timeout=60):
        self.adj_list = {int(k): v for k, v in adj_list.items()}
        self.nodes = sorted(self.adj_list.keys())
        self.num_vertices = len(self.nodes)
        self.timeout = timeout
        self.start_time = None

    def _dsatur_initial_coloring(self):
        if not self.nodes:
            return {}, 0
        saturation = {node: 0 for node in self.nodes}
        degrees = {node: len(self.adj_list.get(node, [])) for node in self.nodes}
        coloring = {}
        uncolored_nodes = set(self.nodes)
        while uncolored_nodes:
            node_to_color = max(uncolored_nodes, key=lambda u: (saturation[u], degrees[u]))
            uncolored_nodes.remove(node_to_color)
            neighbor_colors = {coloring[n] for n in self.adj_list.get(node_to_color, []) if n in coloring}
            color = 1
            while color in neighbor_colors:
                color += 1
            coloring[node_to_color] = color
            for neighbor in self.adj_list.get(node_to_color, []):
                if neighbor in uncolored_nodes:
                    neighbor_neighbor_colors = {coloring[n] for n in self.adj_list.get(neighbor, []) if n in coloring}
                    saturation[neighbor] = len(neighbor_neighbor_colors)
        num_colors = max(coloring.values()) if coloring else 0
        return coloring, num_colors

    def _tabu_search_for_k_colors(self, k, base_coloring, max_iter=10000):
        current_coloring = dict(base_coloring)
        colors_to_nodes = defaultdict(list)
        for node, color in current_coloring.items():
            colors_to_nodes[color].append(node)
        sorted_color_classes = sorted(colors_to_nodes.items(), key=lambda item: len(item[1]))
        if len(sorted_color_classes) > 1:
            color_to_remove = sorted_color_classes[0][0]
            nodes_to_recolor = sorted_color_classes[0][1]
            target_color = sorted_color_classes[1][0]
            for node in nodes_to_recolor:
                current_coloring[node] = target_color
        distinct_colors = sorted(list(set(current_coloring.values())))
        color_map = {old_color: new_color for new_color, old_color in enumerate(distinct_colors, 1)}
        current_coloring = {node: color_map[color] for node, color in current_coloring.items()}
        conflicts = set()
        for u in self.nodes:
            for v in self.adj_list.get(u, []):
                if u < v and current_coloring[u] == current_coloring[v]:
                    conflicts.add(tuple(sorted((u, v))))
        tabu_list = {}
        tabu_tenure = min(15, self.num_vertices // 4 + 1)
        for i in range(max_iter):
            if not conflicts:
                return current_coloring
            if time.time() - self.start_time > self.timeout:
                raise TimeoutError
            best_move = None
            best_delta = float('inf')
            conflicting_nodes = list(set(u for u, v in conflicts).union(v for u, v in conflicts))
            random.shuffle(conflicting_nodes)
            for node in conflicting_nodes:
                current_color = current_coloring[node]
                for new_color in range(1, k + 1):
                    if new_color == current_color:
                        continue
                    if (node, new_color) in tabu_list and tabu_list[(node, new_color)] > i:
                        continue
                    old_conflicts = sum(1 for neighbor in self.adj_list.get(node, []) if current_coloring[neighbor] == current_color)
                    new_conflicts = sum(1 for neighbor in self.adj_list.get(node, []) if current_coloring[neighbor] == new_color)
                    delta = new_conflicts - old_conflicts
                    if delta < best_delta:
                        best_delta = delta
                        best_move = (node, new_color)
            if best_move:
                node_to_move, new_color = best_move
                old_color = current_coloring[node_to_move]
                for neighbor in self.adj_list.get(node_to_move, []):
                    edge = tuple(sorted((node_to_move, neighbor)))
                    if current_coloring[neighbor] == old_color: conflicts.remove(edge)
                    if current_coloring[neighbor] == new_color: conflicts.add(edge)
                current_coloring[node_to_move] = new_color
                tabu_list[(node_to_move, old_color)] = i + tabu_tenure
        return None

    def solve(self):
        self.start_time = time.time()
        best_coloring, k = self._dsatur_initial_coloring()
        if not best_coloring:
            return None, 0
        try:
            for target_k in range(k - 1, 0, -1):
                if time.time() - self.start_time > self.timeout:
                    break
                new_solution = self._tabu_search_for_k_colors(target_k, best_coloring)
                if new_solution:
                    best_coloring = new_solution
                    k = target_k
                else:
                    break
        except TimeoutError:
            pass
        final_coloring_list = [0] * self.num_vertices
        for node, color in best_coloring.items():
            final_coloring_list[node] = color
        return final_coloring_list, k

class NpGcpDInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, ground_truth: Optional[float] = None, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.ground_truth = ground_truth
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "gcp-d"
        self.params = kwargs

    def _generate_single_question(self) -> Tuple[Dict, List[int]]:
        num_vertices = random.randint(*self.params["num_vertices"])
        num_colors = random.randint(*self.params["num_colors"])
        partitions = [[] for _ in range(num_colors)]
        coloring = [-1] * num_vertices
        for i in range(num_vertices):
            color = random.randint(0, num_colors - 1)
            partitions[color].append(i)
            coloring[i] = color + 1
        adj = {str(i): [] for i in range(num_vertices)}
        edge_density = self.params["edge_density"]
        for i in range(num_colors):
            for j in range(i + 1, num_colors):
                for u in partitions[i]:
                    for v in partitions[j]:
                        if random.random() < edge_density:
                            adj[str(u)].append(v)
                            adj[str(v)].append(u)
        final_adj = {str(k): [int(i) for i in v] for k, v in adj.items()}
        return final_adj, coloring

    def case_generator(self) -> Dict[str, Any]:
        identity = {"difficulty": self.difficulty}
        
        graph, _ = self._generate_single_question()
        
        solver = GCPSolver(graph, timeout=10) # Using a 10s timeout for generation
        _, ground_truth = solver.solve()
        
        identity["question"] = graph
        identity["ground_truth"] = ground_truth
        return identity

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/GCP_D/GCP-D.md"
        task_info = extract_markdown_content_NP(md_file)
        
        # Format the graph for the prompt
        graph_str = ""
        sorted_nodes = sorted(identity["question"].keys(), key=int)
        for node in sorted_nodes:
            neighbors = identity["question"][node]
            graph_str += f"{node}: {neighbors}\n"
            
        prompt = get_prompt(self.task_type, task_info, graph_str)
        return prompt

if __name__ == "__main__":
    generator = NpGcpDInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
