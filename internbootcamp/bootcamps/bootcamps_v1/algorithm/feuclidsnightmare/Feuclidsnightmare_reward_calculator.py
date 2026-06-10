import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的其他类 ===

class DisjointSetUnion:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.num_sets = n
        self.done = [0] * n  # 0: not done, 1: done

    def find(self, a):
        acopy = a
        while a != self.parent[a]:
            a = self.parent[a]
        while acopy != a:
            self.parent[acopy], acopy = a, self.parent[acopy]
        return a

    def union(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a != b:
            if self.size[a] < self.size[b]:
                a, b = b, a
            self.parent[b] = a
            self.size[a] += self.size[b]
            self.num_sets -= 1

    def is_done(self, a):
        return self.done[self.find(a)]

    def set_done(self, a):
        self.done[self.find(a)] = 1


class FeuclidsnightmareRewardCalculator(BaseRewardCalculator):
    """Feuclidsnightmare奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        size_line = lines[0].split()
        if len(size_line) != 2:
            return None
        try:
            size = int(size_line[0])
            s_prime_size = int(size_line[1])
        except ValueError:
            return None
        indices_line = lines[1].split()
        try:
            indices = list(map(int, indices_line))
            if len(indices) != s_prime_size:
                return None
        except ValueError:
            return None
        return {
            'size': size,
            's_prime_size': s_prime_size,
            'indices': indices
        }
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        if solution['size'] != identity['correct_size']:
            return False
        if solution['s_prime_size'] != len(identity['correct_indices']):
            return False
        if solution['indices'] != identity['correct_indices']:
            return False
        return True
    
    # 其他额外方法

