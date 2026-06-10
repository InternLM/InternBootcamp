import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import subprocess
from typing import Dict
from typing import Any
from typing import List




class DportalsInstructionGenerator(BaseInstructionGenerator):
    """Dportals Bootcamp指令生成器"""
    
    def __init__(self, max_n=4, max_m=3, max_k=5000):
        """
        初始化Dportals指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_k = min(max_k, 5000)
    
    def case_generator(self) -> Dict[str, Any]:
        n = random.randint(1, self.max_n)
        max_possible_m = min(self.max_m, n*(n-1)//2)
        m = random.randint(0, max_possible_m)
        k = random.randint(0, self.max_k)

        # Generate b values ensuring k + sum(b_i) <= 5000 (problem constraints)
        total_b_max = max(0, 5000 - k)
        total_b_sum = random.randint(0, total_b_max)
        b_values: List[int] = []
        remaining = total_b_sum

        # Distribute b_sum across castles with backtracking
        temp_values = []
        remaining_temp = remaining
        for _ in range(n):
            upper = min(remaining_temp, 5000)
            temp_values.append(upper)
            remaining_temp -= upper
        
        for val in reversed(temp_values):
            if remaining <= 0:
                b_values.append(0)
                continue
            actual = random.randint(0, min(val, remaining))
            b_values.append(actual)
            remaining -= actual
        random.shuffle(b_values)  # Ensure random distribution

        # Generate castles data with possible impossible scenarios
        castles = []
        for i in range(n):
            # Allow a_i to potentially be unattainable
            a_i = random.randint(0, 5000)
            b_i = b_values[i]
            c_i = random.randint(0, 5000)
            castles.append((a_i, b_i, c_i))

        # Generate portals with u > v constraint
        portals = []
        existing_portals = set()
        for _ in range(m):
            while True:
                u = random.randint(2, n)
                v = random.randint(1, u-1)
                if (u, v) not in existing_portals:
                    existing_portals.add((u, v))
                    portals.append((u, v))
                    break

        # Prepare input data for reference solution
        input_lines = [f"{n} {m} {k}"]
        input_lines.extend(f"{a} {b} {c}" for a, b, c in castles)
        input_lines.extend(f"{u} {v}" for u, v in portals)
        input_str = '\n'.join(input_lines)

        # Execute reference solution with validation
        try:
            process = subprocess.run(
                ['python', 'solution.py'],
                input=input_str.encode(),
                capture_output=True,
                timeout=10,
                check=True
            )
            output = process.stdout.decode().strip()
            correct_output = int(output) if output.strip() else -1
        except (subprocess.TimeoutExpired, ValueError, subprocess.CalledProcessError):
            correct_output = -1

        return {
            'n': n,
            'm': m,
            'k': k,
            'castles': castles,
            'portals': portals,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['k']}"
        ]
        input_lines.extend(f"{a} {b} {c}" for a, b, c in question_case['castles'])
        input_lines.extend(f"{u} {v}" for u, v in question_case['portals'])
        input_str = '\n'.join(input_lines)

        problem_desc = f"""You are playing a strategic video game to conquer castles. Rules:
1. Start with k warriors. Conquer castles 1 to n in fixed order.
2. To capture castle i, your army must have ≥a_i warriors (army size remains the same after capture).
3. After capturing castle i, recruit b_i warriors (army increases by b_i).
4. Defend castles by either:
   a) Leaving 1 warrior at current castle, or
   b) Using one-way portals (u > v) from current castle u to v (send 1 warrior).
5. Score is sum of c_i for defended castles. Output -1 if unable to capture all castles.

Input:
{input_str}

Output the maximum possible score. Place your final numerical answer within [answer] and [/answer] tags."""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

