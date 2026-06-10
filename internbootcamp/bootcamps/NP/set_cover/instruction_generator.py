import random
import time
import math
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class SetCoverSolver:
    def __init__(self, universe, subsets, timeout=60):
        self.universe = set(universe)
        self.subsets = {int(k): set(v) for k, v in subsets.items()}
        self.timeout = timeout
        self.start_time = None

    def _greedy_initial_solve(self):
        uncovered = self.universe.copy()
        cover = set()
        available_subsets = self.subsets.copy()
        while uncovered and available_subsets:
            best_subset_id = max(
                available_subsets,
                key=lambda sid: len(uncovered.intersection(available_subsets[sid]))
            )
            cover.add(best_subset_id)
            uncovered -= available_subsets[best_subset_id]
            del available_subsets[best_subset_id]
        return cover

    def _remove_redundant_subsets(self, cover_set):
        current_cover = list(cover_set)
        random.shuffle(current_cover)
        best_cover = set(current_cover)
        for subset_id in current_cover:
            temp_cover = best_cover - {subset_id}
            covered_by_rest = set().union(*(self.subsets.get(sid, set()) for sid in temp_cover))
            if self.universe.issubset(covered_by_rest):
                best_cover.remove(subset_id)
        return best_cover

    def solve(self):
        self.start_time = time.time()
        union_of_all_subsets = set().union(*self.subsets.values())
        if not self.universe.issubset(union_of_all_subsets):
            return "Impossible", 0
        current_solution_set = self._greedy_initial_solve()
        current_solution_set = self._remove_redundant_subsets(current_solution_set)
        best_solution_set = current_solution_set.copy()
        T = 1.0
        T_min = 0.0001
        alpha = 0.995
        while T > T_min and (time.time() - self.start_time) < self.timeout:
            neighbor_set = set()
            if random.random() < 0.6:
                temp_set = current_solution_set.copy()
                if temp_set:
                    subset_to_remove = random.choice(list(temp_set))
                    temp_set.remove(subset_to_remove)
                uncovered_after_removal = self.universe - set().union(*(self.subsets.get(sid, set()) for sid in temp_set))
                if uncovered_after_removal:
                    available_for_repair = {
                        sid: elements for sid, elements in self.subsets.items()
                        if sid not in temp_set and not uncovered_after_removal.isdisjoint(elements)
                    }
                    while uncovered_after_removal and available_for_repair:
                        best_repair_subset = max(available_for_repair,
                            key=lambda sid: len(uncovered_after_removal.intersection(available_for_repair[sid])))
                        temp_set.add(best_repair_subset)
                        uncovered_after_removal -= available_for_repair[best_repair_subset]
                        del available_for_repair[best_repair_subset]
                neighbor_set = temp_set
            else:
                temp_set = current_solution_set.copy()
                unused_subsets = [sid for sid in self.subsets if sid not in temp_set]
                if unused_subsets:
                    subset_to_add = random.choice(unused_subsets)
                    temp_set.add(subset_to_add)
                    neighbor_set = self._remove_redundant_subsets(temp_set)
            if not neighbor_set:
                continue
            uncovered_elements = self.universe - set().union(*(self.subsets.get(sid, set()) for sid in neighbor_set))
            if uncovered_elements:
                continue
            cost_current = len(current_solution_set)
            cost_neighbor = len(neighbor_set)
            delta = cost_neighbor - cost_current
            if delta < 0 or (T > 0 and random.random() < math.exp(-delta / T)):
                current_solution_set = neighbor_set
                if random.random() < 0.1:
                    current_solution_set = self._remove_redundant_subsets(current_solution_set)
                if len(current_solution_set) < len(best_solution_set):
                    best_solution_set = current_solution_set.copy()
            T *= alpha
        best_solution_set = self._remove_redundant_subsets(best_solution_set)
        return sorted(list(best_solution_set)), len(best_solution_set)

class NpSetCoverInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "set-cover"
        self.params = kwargs

    def _generate_single_question(self) -> Tuple[Dict, List[int]]:
        num_elements = random.randint(*self.params["num_elements_range"])
        num_subsets = random.randint(*self.params["num_subsets_range"])
        U = list(range(num_elements))
        S = {}
        max_subset_size = max(1, int(num_elements * self.params["subset_size_factor"]))
        for i in range(num_subsets):
            size = random.randint(1, max_subset_size)
            S[str(i)] = random.sample(U, k=min(size, num_elements))
        covered_elements = set.union(*(set(s) for s in S.values())) if S else set()
        uncovered = set(U) - covered_elements
        if uncovered:
            if S:
                for element in uncovered:
                    random_subset_id = random.choice(list(S.keys()))
                    if element not in S[random_subset_id]:
                        S[random_subset_id].append(element)
            else:
                S[str(len(S))] = list(uncovered)
        answer = sorted([int(k) for k in S.keys()])
        return {"U": sorted(U), "S": S}, answer

    def case_generator(self) -> Dict[str, Any]:
        problem, _ = self._generate_single_question()
        solver = SetCoverSolver(problem["U"], problem["S"], timeout=10)
        _, ground_truth = solver.solve()
        identity = {
            "difficulty": self.difficulty,
            "question": problem,
            "ground_truth": ground_truth
        }
        return identity

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/set_cover/set-cover.md"
        task_info = extract_markdown_content_NP(md_file)
        problem = identity["question"]
        u_str = f"U = {sorted(problem['U'])}"
        s_str = "S = {\n"
        for k, v in sorted(problem['S'].items(), key=lambda item: int(item[0])):
            s_str += f"  {k}: {sorted(v)},\n"
        s_str = s_str.rstrip(",\n") + "\n}"
        question_str = f"{u_str}\n{s_str}"
        prompt = get_prompt(self.task_type, task_info, question_str)
        return prompt

if __name__ == "__main__":
    generator = NpSetCoverInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
