import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
import json
import random
import re
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt, load_prompt_NP_template
class SubsetSumSolver:
    """
    Solves the Subset Sum problem with the objective of maximizing the number
    of elements in the subset. This is solved optimally using Dynamic Programming,
    framing it as a variation of the 0/1 Knapsack problem.
    """
    def __init__(self, numbers, target):
        """
        Initializes the solver.

        Args:
            numbers (list): A list of (index, value) tuples.
            target (int): The target sum.
        """
        self.numbers = sorted(numbers, key=lambda x: x[0])
        self.target = target
        self.num_items = len(self.numbers)

    def solve(self):
        """
        Dispatches to the appropriate solver based on problem size.
        It prioritizes exact solvers and chooses the most efficient one based on
        the problem's characteristics (number of items vs. target value).
        """
        # For a small number of items, Meet-in-the-middle is generally most efficient.
        if self.num_items <= 40:
            # print("   - Using exact Meet-in-the-middle solver.")
            return self._solve_meet_in_the_middle()

        # For a larger number of items, DP is feasible if the target is not too large.
        if self.num_items * self.target <= 2 * 10**7:
            # print("   - Using exact DP solver.")
            return self._solve_dp()

        # If the problem is too large for any exact solver, we cannot guarantee an optimal solution.
        print("   - Problem size too large for any exact solver, no solution can be found.")
        return "No solution", 0

    def _get_subset_sums_max_cardinality(self, number_list):
        """
        Generates all possible subset sums for a given list of numbers,
        optimizing for maximum cardinality for each sum.

        Args:
            number_list: A list of (index, value) tuples.

        Returns:
            A dictionary mapping each possible sum to a tuple of
            (max_cardinality, list_of_indices).
            Example: {sum: (cardinality, [indices])}
        """
        sums = {0: (0, [])}  # Start with sum 0, cardinality 0, empty set
        for index, value in number_list:
            new_sums = {}
            for s, (card, indices) in sums.items():
                new_s = s + value
                new_card = card + 1
                
                # Check if this new sum is an improvement (either new or better cardinality)
                # We check against new_sums to handle cases where multiple items in number_list
                # could form the same new_s. We want the one with highest cardinality.
                if new_s not in sums or new_card > sums[new_s][0]:
                    if new_s not in new_sums or new_card > new_sums[new_s][0]:
                        new_sums[new_s] = (new_card, indices + [index])

            # Merge the improvements into the main sums dictionary
            for s, (card, indices) in new_sums.items():
                if s not in sums or card > sums[s][0]:
                    sums[s] = (card, indices)
        return sums

    def _solve_meet_in_the_middle(self):
        """
        Finds the optimal solution using the Meet-in-the-Middle algorithm.
        This approach is very efficient for a small number of items (e.g., N <= 40).
        """
        if self.target == 0:
            return [], 0

        # 1. Split the numbers into two halves
        mid_index = self.num_items // 2
        first_half = self.numbers[:mid_index]
        second_half = self.numbers[mid_index:]

        # 2. Generate all subset sums for both halves, optimized for max cardinality
        sums_a = self._get_subset_sums_max_cardinality(first_half)
        sums_b = self._get_subset_sums_max_cardinality(second_half)

        # 3. Meet in the middle to find the best combination
        best_cardinality = -1
        best_indices = []

        if self.target in sums_a:
            card, indices = sums_a[self.target]
            best_cardinality = card
            best_indices = indices

        if self.target in sums_b:
            card, indices = sums_b[self.target]
            if card > best_cardinality:
                best_cardinality = card
                best_indices = indices

        for s_a, (card_a, indices_a) in sums_a.items():
            needed_sum = self.target - s_a
            if needed_sum in sums_b:
                card_b, indices_b = sums_b[needed_sum]
                
                current_cardinality = card_a + card_b
                if current_cardinality > best_cardinality:
                    best_cardinality = current_cardinality
                    best_indices = indices_a + indices_b

        if best_cardinality == -1:
            return "No solution", 0
        
        return sorted(best_indices), best_cardinality

    def _solve_dp(self):
        """
        Calculates the optimal subset of numbers that sums to the target
        with the maximum possible number of elements, using Dynamic Programming.
        This implementation is written from scratch based on the problem description.

        Returns:
            A tuple containing:
            - A list of the indices of the selected numbers.
            - The number of elements in the solution subset.
            - "No solution" if no subset sums to the target.
        """
        # dp[i][j] will store the max number of items to get sum j using first i items.
        # Initialize with -1 to indicate "not reachable".
        dp = [[-1 for _ in range(self.target + 1)] for _ in range(self.num_items + 1)]

        # Base case: a sum of 0 is possible with 0 items.
        for i in range(self.num_items + 1):
            dp[i][0] = 0

        # Build the DP table row by row
        for i in range(1, self.num_items + 1):
            _index, num_value = self.numbers[i - 1]
            
            for j in range(1, self.target + 1):
                # Case 1: Don't include the current number (numbers[i-1]).
                # The max cardinality is the same as for the previous i-1 items.
                card_without = dp[i - 1][j]

                # Case 2: Include the current number.
                card_with = -1
                if j >= num_value and dp[i - 1][j - num_value] != -1:
                    card_with = dp[i - 1][j - num_value] + 1
                
                # dp[i][j] is the best we can do with the first i items for sum j.
                dp[i][j] = max(card_without, card_with)
        
        # --- Backtrack to find which numbers were included ---
        max_cardinality = dp[self.num_items][self.target]
        if max_cardinality == -1:
            return "No solution", 0

        selected_indices = []
        # Start from the bottom-right corner of the DP table
        j = self.target
        for i in range(self.num_items, 0, -1):
            _index, num_value = self.numbers[i - 1]
            
            # To reconstruct the path, we check if including the current item was
            # necessary to achieve the optimal cardinality at dp[i][j].
            # This is true if the value at dp[i][j] is different from the value
            # at dp[i-1][j] (the case where we didn't include the item).
            if dp[i][j] != dp[i-1][j]:
                selected_indices.append(_index)
                j -= num_value
        
        return sorted(selected_indices), max_cardinality

    
class NpSubsetSumInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, target: Optional[float] = None, numbers: Optional[List[float]] = None, ground_truth: Optional[float] = None, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.target = target
        self.numbers = numbers
        self.ground_truth = ground_truth
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "subset-sum"
        self.params = kwargs

    def _calculate_ground_truth(self, problem: Dict) -> int:
        target = problem.get('target')
        numbers_dict = problem.get('numbers')

        if target is None or numbers_dict is None:
            return 0
        
        numbers_list = [(int(k), v) for k, v in numbers_dict.items()]
        
        solver = SubsetSumSolver(numbers_list, target)
        _solution, size = solver.solve()
        
        return size

    def _generate_solution_with_sum(self, target_sum: int, solution_size: int, low: int, high: int, max_attempts: int = 200) -> List[int]:
        """在区间[low, high]内生成一个长度为solution_size且和为target_sum的列表"""
        if solution_size <= 0:
            return []
        for _ in range(max_attempts):
            # 先随机生成，再微调到目标和
            vals = [random.randint(low, high) for _ in range(solution_size)]
            s = sum(vals)
            diff = target_sum - s
            # 通过随机调节若干次来逼近目标
            adjust_attempts = 0
            while diff != 0 and adjust_attempts < 500:
                idx = random.randrange(solution_size)
                if diff > 0:
                    inc = min(diff, high - vals[idx])
                    if inc <= 0:
                        adjust_attempts += 1
                        continue
                    vals[idx] += inc
                    diff -= inc
                else:
                    dec = min(-diff, vals[idx] - low)
                    if dec <= 0:
                        adjust_attempts += 1
                        continue
                    vals[idx] -= dec
                    diff += dec
                adjust_attempts += 1
            if sum(vals) == target_sum and all(low <= v <= high for v in vals):
                return vals
        # 失败回退：均匀拆分
        base = target_sum // solution_size
        rem = target_sum % solution_size
        vals = [base] * solution_size
        for i in range(rem):
            vals[i] += 1
        if all(low <= v <= high for v in vals):
            return vals
        raise ValueError("无法在给定范围内生成满足和的解列表")
    def generate_single_question(self) -> Tuple[Dict, List[List[int]]]:
            """
            生成单个子集和问题，并确保存在多个最优解（如果可能）。
            返回：problem, answers_index_sets（多个索引集合）
            """
            num_total = random.randint(*self.params["total_numbers_range"])
            num_solution = random.randint(*self.params["solution_size_range"])
            # 按难度确定目标多解数量范围
            if self.difficulty == "easy":
                desired_min, desired_max = 2, 3
            elif self.difficulty == "medium":
                desired_min, desired_max = 3, 4
            elif self.difficulty == "hard":
                desired_min, desired_max = 4, 5
            elif self.difficulty == "bench":
                desired_min, desired_max = 5, 6
            else:
                desired_min, desired_max = 2, 3  # 默认
            num_variants = random.randint(desired_min, desired_max)
            # 若总位数不足以容纳所有解，降低解的个数
            num_variants = min(num_variants, max(1, num_total // max(1, num_solution)))

            # 约束小数值区间，用于偏向小数确保“基数最大”
            small_high = min(self.params["value_range"][1], self.params["value_range"][0] + 15)
            low, high = self.params["value_range"][0], self.params["value_range"][1]

            # 1) 先生成第一个解，确定target
            solution_values_1 = [random.randint(self.params["value_range"][0], small_high) for _ in range(num_solution)]
            target = sum(solution_values_1)
            solutions_values_list: List[List[int]] = [solution_values_1]

            # 2) 生成另外(num_variants-1)个不同的解，和为同一target
            for _ in range(num_variants - 1):
                for _attempt in range(200):
                    candidate = self._generate_solution_with_sum(target, num_solution, self.params["value_range"][0], small_high)
                    # 要求与已有解的多重集不同
                    def multiset_signature(vals: List[int]) -> Tuple[Tuple[int, int], ...]:
                        m = {}
                        for v in vals:
                            m[v] = m.get(v, 0) + 1
                        return tuple(sorted(m.items()))
                    cand_sig = multiset_signature(candidate)
                    if all(cand_sig != multiset_signature(exist) for exist in solutions_values_list):
                        solutions_values_list.append(candidate)
                        break

            # 3) 生成干扰项
            # 预留出所有解需要的槽位
            required_slots = num_solution * len(solutions_values_list)
            if required_slots > num_total:
                num_total = required_slots
            num_distractors = max(0, num_total - required_slots)
            distractors = [random.randint(low, high) for _ in range(num_distractors)]

            # 4) 合并并打乱，记录各个解在打乱后的索引
            tagged = []
            answer_index_sets: List[List[int]] = []
            for sol_idx, sol_vals in enumerate(solutions_values_list):
                tagged.extend([(v, ('sol', sol_idx)) for v in sol_vals])
            tagged.extend([(v, 'dist') for v in distractors])
            random.shuffle(tagged)

            numbers_dict = {}
            # 使用每个解的编号进行分桶，保证与原始解一一对应
            sol_buckets: List[List[int]] = [[] for _ in range(len(solutions_values_list))]

            for i, (value, tag) in enumerate(tagged):
                numbers_dict[str(i)] = value
                if isinstance(tag, tuple) and tag[0] == 'sol':
                    sol_idx = tag[1]
                    sol_buckets[sol_idx].append(i)

            # 归并答案索引
            answer_index_sets = [sorted(bucket) for bucket in sol_buckets if len(bucket) == num_solution]

            problem = {"target": target, "numbers": numbers_dict}
            return problem, answer_index_sets
        
    def case_generator(self) -> Dict[str, Any]:
        identity = {}
        identity["difficulty"] = self.difficulty
        if self.difficulty == "easy":
            self.params["total_numbers_range"] = (5, 10)
            self.params["solution_size_range"] = (4, 8)
            self.params["value_range"] = (1, 5)
            self.current_difficulty = "easy"
        elif self.difficulty == "medium":
            self.params["total_numbers_range"] = (8, 12)
            self.params["solution_size_range"] = (4, 8)
            self.params["value_range"] = (1, 10)
            self.current_difficulty = "medium"
        elif self.difficulty == "hard":
            self.params["total_numbers_range"] = (12, 15)
            self.params["solution_size_range"] = (8, 12)
            self.params["value_range"] = (1, 15)
            self.current_difficulty = "hard"
        elif self.difficulty == "bench":
            self.params["total_numbers_range"] = (15, 20)
            self.params["solution_size_range"] = (10, 15)
            self.params["value_range"] = (1, 15)
            self.current_difficulty = "bench"

        problem, self.answer_index_sets = self.generate_single_question()

        # Calculate ground_truth using the solver
        ground_truth = self._calculate_ground_truth(problem)
        identity["ground_truth"] = ground_truth
        
        identity["question"] = problem["target"]
        identity["numbers"] = problem["numbers"]
        return identity
    
    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/subset_sum/subset-sum.md"
        task_info = extract_markdown_content_NP(md_file)
        prompt = get_prompt(self.task_type, task_info, identity["question"])
        return prompt

if __name__ == "__main__":
    generator = NpSubsetSumInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print(identity)
    prompt = generator.prompt_func(identity)
    print(prompt)