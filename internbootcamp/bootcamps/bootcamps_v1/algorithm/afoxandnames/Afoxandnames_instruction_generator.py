import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import json




class AfoxandnamesInstructionGenerator(BaseInstructionGenerator):
    """Afoxandnames Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Afoxandnames指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 3)  # Number of names
        self.names = params.get('names', self.generate_random_names(self.n))
    
    def case_generator(self):
        """Generate a puzzle instance with random names"""
        # Generate random names and ensure they can form a valid order
        names = []
        while True:
            names = self.generate_random_names(self.n)
            # Check if these names can form a valid order
            valid = True
            for i in range(len(names) - 1):
                if len(names[i]) == len(names[i+1]):
                    if names[i] > names[i+1]:
                        valid = False
                        break
                else:
                    if not (names[i] < names[i+1]):
                        valid = False
                        break
            if valid:
                break
        
        # Shuffle the names to create a puzzle instance
        shuffled_names = names.copy()
        random.shuffle(shuffled_names)
        
        return {
            'n': self.n,
            'names': shuffled_names
        }
    
    @staticmethod
    def prompt_func(question_case):
        names = question_case['names']
        names_str = ', '.join(names)
        prompt = (
            "你是一名科学家，Fox Ciel，正在准备提交一篇论文。你需要确保作者列表按某种字母顺序排列。给你一组名字："
            f"{names_str}，判断是否存在一种字母顺序，使得这些名字按字典序排列。如果存在，输出该顺序；否则，输出'Impossible'。"
            "注意：名字的比较规则是逐字符比较，遇到第一个不同的字符按字母顺序决定大小。如果一个名字是另一个的前缀，则较短的名字排在前面。"
            "请将答案放在[answer]和[/answer]之间。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_random_names(self, n=3):
        """Generate random names for testing"""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        names = []
        for _ in range(n):
            length = random.randint(3, 6)
            name = ''.join(random.choice(letters) for _ in range(length))
            names.append(name)
        return names

    @staticmethod
    def topological_sort(graph):
        visited = set()
        stack = []
        has_cycle = [False]

        def dfs(node):
            visited.add(node)
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor in visited:
                        has_cycle[0] = True
                        return
                    if neighbor not in visited:
                        dfs(neighbor)
            stack.append(node)

        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char not in visited:
                dfs(char)
                if has_cycle[0]:
                    return -1
        return ''.join(stack[::-1])

    @staticmethod
    def is_ordered(a, b, order_dict):
        min_len = min(len(a), len(b))
        for i in range(min_len):
            if a[i] != b[i]:
                return order_dict[a[i]] < order_dict[b[i]]
        return len(a) <= len(b)
