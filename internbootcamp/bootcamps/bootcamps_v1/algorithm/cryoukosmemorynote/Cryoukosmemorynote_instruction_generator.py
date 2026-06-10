import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any




class CryoukosmemorynoteInstructionGenerator(BaseInstructionGenerator):
    """Cryoukosmemorynote Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_m=20):
        """
        初始化Cryoukosmemorynote指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，默认最大页面数为20，最大序列长度为20。
        """
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成谜题实例，包含n, m和页面序列a。
        """
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        a = [random.randint(1, n) for _ in range(m)]
        return {
            'n': n,
            'm': m,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将谜题实例转换为详细的自然语言问题描述。
        """
        n = question_case['n']
        m = question_case['m']
        a = ' '.join(map(str, question_case['a']))
        problem_text = f"""你是Ryouko，需要解决一个关于记忆笔记本页面优化的问题。你的笔记本共有{n}页，编号从1到{n}。你需要按顺序查阅以下页面序列（共{m}次）：{a}。

每次翻页的代价是当前页与目标页的绝对差值。你最多可以执行一次合并操作：选择一个页面x合并到页面y，使得所有在序列中的x都会被替换为y。请计算经过最优合并后最小的总翻页代价。

例如，当输入为：
4 6
1 2 3 4 3 2
时，合并页面4到3后，总代价为3，因此最终答案为3。

你的任务是解决以下具体案例：
- 笔记本总页数n = {n}
- 序列长度m = {m}
- 访问序列a = {a}

请将最终答案的整数值放置在[answer]和[/answer]标签之间。例如：[answer]42[/answer]"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_turns(n: int, m: int, a: list) -> int:
        """
        计算给定案例的最小翻页数。
        """
        if m <= 1:
            return 0

        original_cost = sum(abs(a[i] - a[i-1]) for i in range(1, m))
        adj = [[] for _ in range(n+1)]  # 邻接关系存储

        # 构建邻接关系
        for i in range(m):
            current = a[i]
            if i > 0 and a[i-1] != current:
                adj[current].append(a[i-1])
            if i < m-1 and a[i+1] != current:
                adj[current].append(a[i+1])

        max_reduction = 0
        for page in range(1, n+1):
            neighbors = adj[page]
            if not neighbors:
                continue

            # 计算原始总代价
            original_sum = sum(abs(page - x) for x in neighbors)

            # 计算最优合并后的代价
            sorted_neighbors = sorted(neighbors)
            median_index = len(sorted_neighbors) // 2
            median = sorted_neighbors[median_index]
            optimized_sum = sum(abs(median - x) for x in sorted_neighbors)

            # 更新最大减少量
            current_reduction = original_sum - optimized_sum
            if current_reduction > max_reduction:
                max_reduction = current_reduction

        return original_cost - max_reduction
