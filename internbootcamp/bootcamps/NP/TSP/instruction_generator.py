import random
import time
import numpy as np
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class TSPSolver:
    def __init__(self, dist_matrix, timeout=60):
        self.dist_matrix = dist_matrix
        self.num_cities = dist_matrix.shape[0]
        self.timeout = timeout
        self.start_time = None

    def _calculate_tour_distance(self, tour):
        return sum(self.dist_matrix[tour[i], tour[(i + 1) % self.num_cities]] for i in range(self.num_cities))

    def _initial_tour(self):
        min_dist = float('inf')
        best_tour = []
        for start_node in range(self.num_cities):
            tour = [start_node]
            unvisited = set(range(self.num_cities)) - {start_node}
            current = start_node
            while unvisited:
                nearest = min(unvisited, key=lambda n: self.dist_matrix[current, n])
                unvisited.remove(nearest)
                tour.append(nearest)
                current = nearest
            dist = self._calculate_tour_distance(tour)
            if dist < min_dist:
                min_dist, best_tour = dist, tour
        return best_tour, min_dist

    def _run_2opt(self, initial_tour):
        best_tour, best_dist = list(initial_tour), self._calculate_tour_distance(initial_tour)
        improved = True
        while improved:
            if time.time() - self.start_time > self.timeout: break
            improved, best_delta, best_swap = False, 0, None
            for i in range(self.num_cities - 1):
                for j in range(i + 2, self.num_cities):
                    u1, v1 = best_tour[i], best_tour[i+1]
                    u2, v2 = best_tour[j], best_tour[(j+1) % self.num_cities]
                    delta = (self.dist_matrix[u1, u2] + self.dist_matrix[v1, v2]) - \
                            (self.dist_matrix[u1, v1] + self.dist_matrix[u2, v2])
                    if delta < best_delta:
                        best_delta, best_swap = delta, (i, j)
            if best_swap:
                i, j = best_swap
                best_tour[i+1:j+1] = reversed(best_tour[i+1:j+1])
                best_dist += best_delta
                improved = True
        return best_tour, best_dist
    
    def solve(self):
        self.start_time = time.time()
        initial_tour, _ = self._initial_tour()
        final_tour, final_distance = self._run_2opt(initial_tour)
        return final_tour, final_distance

class NpTspInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "TSP"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        num_cities = random.randint(*self.params["num_cities"])
        
        dist_matrix = np.zeros((num_cities, num_cities))
        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                dist = random.randint(*self.params["distance_range"])
                dist_matrix[i, j] = dist_matrix[j, i] = dist
        
        question = {str(i): {str(j): int(dist_matrix[i, j]) for j in range(num_cities)} for i in range(num_cities)}

        solver = TSPSolver(dist_matrix, timeout=5)
        _, ground_truth = solver.solve()

        return {"difficulty": self.difficulty, "question": question, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/TSP/TSP.md"
        task_info = extract_markdown_content_NP(md_file)
        
        q = identity["question"]
        question_str = ""
        for i in sorted(q.keys(), key=int):
            question_str += f"{i}: {q[i]}\n"
            
        prompt = get_prompt(self.task_type, task_info, question_str.strip())
        return prompt

if __name__ == "__main__":
    generator = NpTspInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
