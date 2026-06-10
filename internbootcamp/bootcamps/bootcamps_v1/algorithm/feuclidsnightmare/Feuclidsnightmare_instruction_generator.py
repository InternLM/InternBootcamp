import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class FeuclidsnightmareInstructionGenerator(BaseInstructionGenerator):
    """Feuclidsnightmare Bootcamp指令生成器"""
    
    def __init__(self, min_m=2, max_m=5, min_n=1, max_n=10, **kwargs):
        """
        初始化Feuclidsnightmare指令生成器
        
        Args:
            min_m: 参数描述
            max_m: 参数描述
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_m = min_m
        self.max_m = max_m
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        m = random.randint(self.min_m, self.max_m)
        all_vectors = []
        # Generate all possible single-coordinate vectors
        for x in range(1, m + 1):
            all_vectors.append({'k': 1, 'x': [x]})
        # Generate all possible two-coordinate vectors, sorted
        for x in range(1, m + 1):
            for y in range(x + 1, m + 1):
                all_vectors.append({'k': 2, 'x': [x, y]})
        max_possible_n = len(all_vectors)
        if max_possible_n == 0:
            max_possible_n = 1
        n_min = max(self.min_n, 1)
        n_max = min(self.max_n, max_possible_n)
        if n_min > n_max:
            n_min = 1
            n_max = max_possible_n
        n = random.randint(n_min, n_max)
        selected_vectors = random.sample(all_vectors, n)
        random.shuffle(selected_vectors)
        vectors_0based = []
        for vec in selected_vectors:
            if vec['k'] == 1:
                x = vec['x'][0]
                vectors_0based.append([x - 1])
            else:
                x, y = vec['x']
                vectors_0based.append([x - 1, y - 1])
        # Compute correct size_mod
        uf1 = DisjointSetUnion(m)
        dims = 0
        for e in vectors_0based:
            if len(e) == 1:
                x = e[0]
                if not uf1.is_done(x):
                    uf1.set_done(x)
                    dims += 1
            elif len(e) == 2:
                x, y = e
                if uf1.find(x) != uf1.find(y):
                    dx = uf1.is_done(x)
                    dy = uf1.is_done(y)
                    both = dx and dy
                    done = dx or dy
                    uf1.union(x, y)
                    if not both:
                        dims += 1
                    if done:
                        uf1.set_done(x)
        size_mod = pow(2, dims, MOD)
        # Compute ans list
        uf2 = DisjointSetUnion(m)
        current_dims = 0
        ans = []
        for i, e in enumerate(vectors_0based, start=1):
            if current_dims == dims:
                break
            if len(e) == 1:
                x = e[0]
                if not uf2.is_done(x):
                    uf2.set_done(x)
                    current_dims += 1
                    ans.append(i)
            elif len(e) == 2:
                x, y = e
                if uf2.find(x) != uf2.find(y):
                    dx = uf2.is_done(x)
                    dy = uf2.is_done(y)
                    both = dx and dy
                    done = dx or dy
                    uf2.union(x, y)
                    if not both:
                        current_dims += 1
                        ans.append(i)
                    if done:
                        uf2.set_done(x)
        # Ensure the indices are sorted in the answer
        ans = sorted(ans)
        return {
            'n': n,
            'm': m,
            'vectors': selected_vectors,
            'correct_size': size_mod,
            'correct_indices': ans
        }
    
    @staticmethod
    def prompt_func(question_case):
        vectors_desc = []
        for vec in question_case['vectors']:
            k = vec['k']
            coords = ' '.join(map(str, vec['x']))
            vectors_desc.append(f"{k} {coords}")
        vectors_str = '\n'.join(vectors_desc)
        prompt = f"""You are the mathematician Euclid, tasked with solving a vector space problem over Z₂. Given a set S of {question_case['n']} vectors in {question_case['m']}-dimensional space, where each vector has at most 2 coordinates set to 1, determine two things:

1. The size of the set T, which consists of all possible vectors obtainable by summing subsets of S (modulo 10⁹+7).
2. The smallest subset S' of S such that every vector in T can be expressed as a sum of elements from S'. If multiple such subsets exist, choose the lexicographically smallest one based on their original order in the input.

Input:
The first line contains two integers n and m.
The next n lines describe each vector with a value k followed by k distinct coordinates (1-based).

Output:
Two lines. The first line contains |T| mod 10⁹+7 and the size of S'. The second line lists the indices of S' in ascending order.

Sample Input:
{question_case['n']} {question_case['m']}
{vectors_str}

Enclose your final answer within [answer] and [/answer] tags. For example:

[answer]
4 2
1 2
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

