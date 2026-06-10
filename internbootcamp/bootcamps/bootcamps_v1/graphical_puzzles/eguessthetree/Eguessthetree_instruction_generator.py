import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class EguessthetreeInstructionGenerator(BaseInstructionGenerator):
    """Eguessthetree Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Eguessthetree指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = params.get('n_range', (1, 24))
        self.min_n = max(1, self.n_range[0])
        self.max_n = min(24, self.n_range[1])
        self.yes_prob = params.get('yes_prob', 0.5)
    
    def case_generator(self):
        for _ in range(100):  # 安全生成循环
            generate_yes = random.random() < self.yes_prob
            n = self._generate_initial_n(generate_yes)
            
            if generate_yes:
                if case := self._generate_valid_case(n):
                    return case
            else:
                if case := self._generate_invalid_case(n):
                    return case
        
        # 默认返回简单案例
        return {'n': 2, 'c': [1,1], 'expected_answer': 'NO'}
    
    @staticmethod
    def prompt_func(question_case):
        return (
            f"Determine if a rooted tree exists with {question_case['n']} nodes where:\n"
            f"- Each internal node has ≥2 children\n"
            f"- Node i's subtree size is exactly {question_case['c']}\n"
            f"Answer with [answer]YES[/answer] or [answer]NO[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_initial_n(self, yes_case):
        if yes_case:
            return random.choice([n for n in range(self.min_n, self.max_n+1) if n ==1 or n>=3])
        return random.randint(self.min_n, self.max_n)

    def _generate_valid_case(self, n):
        if n == 1:
            return {'n':1, 'c':[1], 'expected_answer':'YES'}

        # 生成符合约束的树结构
        root = n
        children = self._split_subtrees(n-1)
        c = [root] + children
        random.shuffle(c)
        return {'n':n, 'c':c, 'expected_answer':'YES'}

    def _split_subtrees(self, total):
        if total == 0:
            return []
        if total == 1:
            return [1]

        # 至少分割为两个子树且每个>=1
        k = random.randint(2, total)
        parts = []
        while sum(parts) < total:
            remain = total - sum(parts)
            max_part = min(remain - (k - len(parts) - 1), remain)
            part = random.randint(1, max_part)
            parts.append(part)

        # 确保内部节点有足够子节点
        return [p if p >=2 else 1 for p in parts]

    def _generate_invalid_case(self, n):
        for _ in range(100):
            # 类型1: 缺少根节点
            if random.random() < 0.5:
                c = [random.randint(1, n-1) for _ in range(n)]
                if n not in c:
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

            # 类型2: 存在根节点但结构冲突
            else:
                c = [n] + random.choices([1,1,2,3], k=n-1)
                if not self._is_valid_solution(n, c):
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

        return {'n':2, 'c':[1,1], 'expected_answer':'NO'}

    def _is_valid_solution(self, n, c):
        # 快速预检查
        if sum(c) != n*(n+1)//2 and n > 1:  # 修正总和验证逻辑
            return False

        # 完整回溯验证
        avail = defaultdict(int)
        for num in c:
            if num > n:
                return False
            avail[num] += 1

        try:
            self._backtrack(avail, [], sum(c), n)
            return False
        except self.SolutionFound:
            return True

    def _backtrack(self, avail, stack, sumleft, n):
        if not stack and sumleft == 0:
            raise self.SolutionFound()

        # 添加叶子节点分支
        if avail[1] > 0:
            avail[1] -= 1
            self._backtrack(avail, stack + [1], sumleft - 1, n)
            avail[1] += 1

        # 合并子树分支
        if len(stack) >= 2:
            s = 0
            for i in range(1, len(stack)+1):
                s += stack[-i]
                if s > n:
                    break
                if avail[s] > 0:
                    avail[s] -= 1
                    self._backtrack(avail, stack[:-i] + [s], sumleft - s, n)
                    avail[s] += 1
