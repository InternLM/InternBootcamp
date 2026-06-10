import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CnezzarandnicebeatmapInstructionGenerator(BaseInstructionGenerator):
    """Cnezzarandnicebeatmap Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Cnezzarandnicebeatmap指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，允许自定义点的数量n。
        """
        self.n = n
    
    def case_generator(self):
        """
        生成n个不同的点，并使用贪心算法生成有效排列。确保每个生成的实例都有解。
        """
        while True:
            n = self.n
            points = []
            # 生成n个不重复的点
            while len(points) < n:
                x = random.randint(-10**9, 10**9)
                y = random.randint(-10**9, 10**9)
                if (x, y) not in points:
                    points.append((x, y))
            # 生成排列并验证
            try:
                permutation = self.generate_permutation(n, points)
                if self._verify_correction(permutation, {'n': n, 'points': points}):
                    return {'n': n, 'points': points}
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        生成符合题目要求的详细问题描述，明确答案格式。
        """
        n = question_case['n']
        points = question_case['points']
        problem = [
            "Nezzar wants to reorder points to form a 'nice' beatmap where each triplet has an angle <90° at the center point.",
            f"Given {n} distinct points:"
        ]
        for idx, (x, y) in enumerate(points, 1):
            problem.append(f"Point {idx}: ({x}, {y})")
        problem.append(
            "Output a valid permutation (space-separated numbers) or -1 if impossible.\n"
            "Put your answer within [answer] and [/answer], e.g., [answer]1 2 3[/answer]."
        )
        return '\n'.join(problem) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_permutation(n, points):
        """
        参考解题算法生成排列，正确处理1-based到0-based的索引转换。
        """
        used = [False] * (n + 1)  # 使用1-based索引
        permutation = []
        pre = 1  # 初始化为第一个点（1-based）
        used[pre] = True
        permutation.append(pre)

        for _ in range(n - 1):
            max_dist = -1
            curr = pre
            for i in range(1, n + 1):  # 遍历所有1-based索引
                if not used[i]:
                    # 计算当前点（pre）到候选点i的距离
                    dx = points[i-1][0] - points[pre-1][0]  # 转换为0-based索引
                    dy = points[i-1][1] - points[pre-1][1]
                    dist = dx * dx + dy * dy
                    if dist > max_dist:
                        max_dist = dist
                        curr = i
            permutation.append(curr)
            used[curr] = True
            pre = curr
        return permutation
