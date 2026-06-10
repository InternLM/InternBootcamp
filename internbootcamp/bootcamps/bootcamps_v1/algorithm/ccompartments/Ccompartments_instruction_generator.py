import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcompartmentsInstructionGenerator(BaseInstructionGenerator):
    """Ccompartments Bootcamp指令生成器"""
    
    def __init__(self, max_compartments=10, **params):
        """
        初始化Ccompartments指令生成器
        
        Args:
            max_compartments: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_compartments = max_compartments
    
    def case_generator(self):
        while True:
            n = random.randint(1, self.max_compartments)
            a = [random.randint(0, 4) for _ in range(n)]
            if sum(a) >= 1:
                return {"n": n, "a": a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        a = question_case["a"]
        a_str = " ".join(map(str, a))
        problem = (
            "A team of students is traveling in a train with several compartments. Each compartment currently has some students.\n"
            "They need to rearrange seats such that each compartment ends with 0, 3, or 4 students. Each swap requires convincing a non-student.\n"
            "Your task is to find the minimal number of non-students to convince, or output -1 if impossible.\n\n"
            f"Input Format:\n- First line: {n} (number of compartments)\n- Second line: {a_str} (students per compartment)\n\n"
            "Output the minimal number of swaps or -1. Place your answer within [answer]...[/answer] tags."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_persuasion(a):
        counts = [0] * 5
        for num in a:
            counts[num] += 1
        res = 0

        # Pair 1s and 2s optimally
        t = min(counts[1], counts[2])
        res += t
        counts[1] -= t
        counts[2] -= t
        counts[3] += t

        # Process remaining 1s or 2s
        if counts[1] > 0:
            # Handle groups of 3 remaining 1s
            t = counts[1] // 3
            res += t * 2
            counts[3] += t
            counts[1] %= 3
        elif counts[2] > 0:
            # Handle groups of 3 remaining 2s
            t = counts[2] // 3
            res += t * 2
            counts[3] += t * 2
            counts[2] %= 3

        remaining_1 = counts[1]
        remaining_2 = counts[2]

        # Handle remaining cases
        if remaining_1 == 0:
            if remaining_2 == 1:
                if counts[4] >= 1:
                    res += 1
                elif counts[3] >= 2:
                    res += 2
                else:
                    return -1
            elif remaining_2 == 2:
                res += 2
            elif remaining_2 > 0:
                return -1
        elif remaining_1 == 1:
            if remaining_2 == 1:
                res += 1
            elif remaining_2 == 2:
                if counts[4] >= 1:
                    res += 2
                elif counts[3] >= 1:
                    res += 3
                else:
                    return -1
            elif remaining_2 == 0:
                if counts[3] >= 1:
                    res += 1
                elif counts[4] >= 2:
                    res += 2
                else:
                    return -1
            else:
                return -1
        elif remaining_1 == 2:
            if remaining_2 == 0:
                if counts[4] >= 1:
                    res += 2
                elif counts[3] >= 2:
                    res += 2
                else:
                    return -1
            elif remaining_2 in (1, 2):
                res += 2
            else:
                return -1
        else:
            return -1

        # Check if any remaining students after processing
        if counts[1] > 0 or counts[2] > 0:
            return -1
        return res
