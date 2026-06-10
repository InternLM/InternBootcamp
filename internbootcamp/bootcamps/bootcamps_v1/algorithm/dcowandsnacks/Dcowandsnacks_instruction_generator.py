import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DcowandsnacksInstructionGenerator(BaseInstructionGenerator):
    """Dcowandsnacks Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_k=20):
        """
        初始化Dcowandsnacks指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k
    
    def case_generator(self):
        # 修正k生成逻辑，确保符合题目输入要求
        n = random.randint(2, self.max_n)
        k = random.randint(1, self.max_k)  # 允许k超出n*(n-1)
        
        guests = []
        for _ in range(k):
            # 允许重复的口味组合
            x = random.randint(1, n)
            y = random.randint(1, n)
            while y == x:
                y = random.randint(1, n)
            guests.append([x, y])
        return {'n': n, 'k': k, 'guests': guests}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        guests = question_case['guests']
        problem = (
            "作为农场主John的助手Bessie，你需要安排客人顺序以最小化伤心人数。规则如下：\n\n"
            "1. 共有n种零食（1到n编号），每种恰好一个\n"
            "2. 每位客人有两个不同的偏爱口味\n"
            "3. 客人按顺序依次吃掉自己偏爱口味的剩余零食\n"
            "4. 如果没有剩余偏爱零食，客人会伤心\n\n"
            "输入格式：\n"
            f"第一行：{n} {k}\n"
            f"随后{k}行每行两个整数表示客人喜好\n\n"
            "当前问题：\n"
            f"{n} {k}\n"
        )
        for guest in guests:
            problem += f"{guest[0]} {guest[1]}\n"
        problem += "\n请输出最小的可能伤心人数，并将答案放在[answer]和[/answer]之间。"
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_min_sad(n, k, guests):
        # 重构验证算法
        flavor_map = [[] for _ in range(n)]
        guest_pairs = []

        for idx, (a, b) in enumerate(guests):
            a_idx = a - 1
            b_idx = b - 1
            flavor_map[a_idx].append(idx)
            flavor_map[b_idx].append(idx)
            guest_pairs.append((a_idx, b_idx))

        activated = [False] * n
        visited = [False] * k
        happy_count = 0

        for i in range(k):
            if visited[i]:
                continue
            stack = [i]
            visited[i] = True

            while stack:
                current = stack.pop()
                f1, f2 = guest_pairs[current]

                if not activated[f1] or not activated[f2]:
                    happy_count += 1
                    if not activated[f1]:
                        activated[f1] = True
                        for g in flavor_map[f1]:
                            if not visited[g]:
                                visited[g] = True
                                stack.append(g)
                    if not activated[f2]:
                        activated[f2] = True
                        for g in flavor_map[f2]:
                            if not visited[g]:
                                visited[g] = True
                                stack.append(g)

        return k - happy_count
