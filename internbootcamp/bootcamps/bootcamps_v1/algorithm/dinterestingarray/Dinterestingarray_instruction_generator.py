import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DinterestingarrayInstructionGenerator(BaseInstructionGenerator):
    """Dinterestingarray Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dinterestingarray指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = params.get('n_range', (3, 10))
        self.m_range = params.get('m_range', (2, 6)) 
        self.bit_width = params.get('bit_width', 8)
        self.qi_max = (1 << self.bit_width) - 1
        self.solvable_prob = params.get('solvable_prob', 0.5)
    
    def case_generator(self):
        """重构的案例生成逻辑，保证有效性"""
        n = random.randint(*self.n_range)
        m = random.randint(*self.m_range)
        
        # 生成初始有效约束集
        base_case = self._generate_solvable_case(n, m)
        if random.random() < self.solvable_prob:
            return base_case
        
        # 构造矛盾案例：添加不兼容的约束
        conflict_case = self._add_conflict_constraint(base_case)
        solution_exists, possible_a = self._validate_case(conflict_case)
        return {
            **conflict_case,
            'solution_exists': solution_exists,
            'possible_a': possible_a
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['m']}"]
        for l, r, q in question_case['constraints']:
            input_lines.append(f"{l} {r} {q}")
        input_section = "\n".join(input_lines)
        
        prompt = f"""Solve the array puzzle with bitwise AND constraints. 

Problem Statement:
- Array length: {question_case['n']}
- Number of constraints: {question_case['m']}
- Constraints (l, r, q format):
{input_section}

Requirements:
1. Determine if there exists an array of {question_case['n']} non-negative integers satisfying ALL constraints
2. Each constraint requires: a[l] AND a[l+1] AND ... AND a[r] = q
3. If exists, output "YES" followed by the array elements
4. If not exists, output "NO"

Format your final answer within [answer] tags like:
[answer]
YES
5 3 7 2
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_solvable_case(self, n, m):
        """生成必定有解的案例"""
        a = [random.randint(0, self.qi_max) for _ in range(n)]
        constraints = []
        for _ in range(m-1):
            l = random.randint(1, n)
            r = random.randint(l, n)
            current_and = a[l-1]
            for i in range(l, r):
                current_and &= a[i]
            constraints.append((l, r, current_and))

        # 添加全局约束保证解存在
        constraints.append((1, n, current_and))
        return {
            'n': n,
            'm': m,
            'constraints': constraints,
            'solution_exists': True,
            'possible_a': a
        }

    def _add_conflict_constraint(self, case):
        """添加矛盾约束"""
        # 复制原有约束
        new_constraints = case['constraints'][:]
        l, r = self._find_overlap_interval(new_constraints)

        # 生成矛盾的约束值
        original_q = new_constraints[0][2]
        conflict_q = original_q ^ (1 << random.randint(0, self.bit_width-1))

        # 添加新约束
        new_constraints.append((l, r, conflict_q))
        return {
            'n': case['n'],
            'm': case['m'] + 1,
            'constraints': new_constraints
        }

    def _find_overlap_interval(self, constraints):
        """找到多个约束的重叠区间"""
        intervals = [(l, r) for l, r, _ in constraints]
        max_l = max(l for l, _ in intervals)
        min_r = min(r for _, r in intervals)
        if max_l <= min_r:
            return (max_l, min_r)
        return (1, constraints[0][0])  # 默认返回第一个约束的区间

    def _validate_case(self, case):
        """科学校验案例有效性"""
        n = case['n']
        constraints = case['constraints']

        # 初始化各bit位的允许范围
        bit_masks = [0xFFFFFFFF for _ in range(n)]

        # 应用所有约束
        for l, r, q in constraints:
            for i in range(l-1, r):
                bit_masks[i] &= q

        # 检查所有位置是否可能
        for i in range(n):
            if bit_masks[i] == 0 and not any(
                (l-1 <= i <= r-1 and q == 0) 
                for l, r, q in constraints
            ):
                return False, None

        # 验证约束一致性
        for l, r, q in constraints:
            required_bits = q
            possible_and = 0xFFFFFFFF
            for i in range(l-1, r):
                possible_and &= bit_masks[i]
            if (possible_and & required_bits) != required_bits:
                return False, None

        # 构造可行解
        solution = [random.randint(0, mask) & mask for mask in bit_masks]
        return True, solution
