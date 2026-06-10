import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EhelpingpeopleInstructionGenerator(BaseInstructionGenerator):
    """Ehelpingpeople Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_q=3, max_initial=100):
        """
        初始化Ehelpingpeople指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_initial: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_initial = max_initial
    
    def case_generator(self):
        class RangeNode:
            def __init__(self, l, r, prob):
                self.l = l
                self.r = r
                self.prob = round(prob, 3)
                self.children = []
        
        def build_hierarchy(n, q):
            root = RangeNode(1, n, 0.0)
            nodes = [root]
            
            def add_children(parent, depth):
                if len(nodes) >= q or depth > 3:
                    return
                
                # Generate contained intervals
                if random.random() < 0.7:
                    cl = random.randint(parent.l, parent.r)
                    cr = random.randint(cl, parent.r)
                    if cr - cl >= 1:
                        child = RangeNode(cl, cr, random.uniform(0, 1))
                        parent.children.append(child)
                        nodes.append(child)
                        add_children(child, depth+1)
                
                # Generate adjacent intervals
                if random.random() < 0.3 and parent.r < n:
                    split = random.randint(parent.l, parent.r)
                    if split < parent.r:
                        left = RangeNode(parent.l, split, random.uniform(0, 1))
                        right = RangeNode(split+1, parent.r, random.uniform(0, 1))
                        parent.children.extend([left, right])
                        nodes.extend([left, right])
                        add_children(left, depth+1)
                        add_children(right, depth+1)
            
            add_children(root, 0)
            return nodes[:q]
        
        while True:
            try:
                n = random.randint(3, self.max_n)
                q = random.randint(2, self.max_q)
                a = [random.randint(0, self.max_initial) for _ in range(n)]
                nodes = build_hierarchy(n, q)
                
                # Validate hierarchy structure
                stack = [(nodes[0].l, nodes[0].r)]
                for node in nodes[1:]:
                    while stack and not (stack[-1][0] <= node.l and node.r <= stack[-1][1]):
                        stack.pop()
                    if not stack:
                        raise ValueError("Invalid interval structure")
                    stack.append((node.l, node.r))
                
                recommendations = [(node.l, node.r, node.prob) for node in nodes[1:]]  # Skip root
                expected = self._calculate(n, a, recommendations)
                return {
                    "n": n,
                    "q": len(recommendations),
                    "a": a,
                    "recommendations": recommendations,
                    "correct_output": expected
                }
            except:
                continue
    
    @staticmethod
    def prompt_func(case):
        input_str = f"{case['n']} {case['q']}\n"
        input_str += " ".join(map(str, case["a"])) + "\n"
        for l, r, p in case["recommendations"]:
            input_str += f"{l} {r} {p:.3f}\n"
        return f"""Calculate the expected maximum money value with exact formatting. Enclose your final answer in [answer] and [/answer].

Input:
{input_str.strip()}

Requirements:
1. Output must have exactly 9 decimal places
2. Use format [answer]X.xxxxxxxxx[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _calculate(self, n, a, recommendations):
        class Segment:
            def __init__(self, a, b, p):
                self.a = a-1  # 0-based
                self.b = b-1
                self.p = p
                self.children = []
                self.maxv = 0
                self.dist = {}

            def solve(self, values):
                # Calculate base maximum
                self.maxv = max(values[self.a:self.b+1])

                # Process children
                prev_end = self.a-1
                for child in self.children:
                    # Left gap
                    if prev_end+1 <= child.a-1:
                        self.maxv = max(self.maxv, max(values[prev_end+1:child.a]))
                    # Child's maximum (after solving)
                    child.solve(values)
                    self.maxv = max(self.maxv, child.maxv)
                    prev_end = child.b
                # Right gap
                if prev_end+1 <= self.b:
                    self.maxv = max(self.maxv, max(values[prev_end+1:self.b+1]))

                # Initialize distribution
                self.dist = {self.maxv: 1.0}

                # Merge children distributions
                for child in self.children:
                    new_dist = {}
                    for k1, p1 in self.dist.items():
                        for k2, p2 in child.dist.items():
                            key = max(k1, k2)
                            prob = p1 * p2
                            new_dist[key] = new_dist.get(key, 0.0) + prob
                    self.dist = new_dist

                # Apply current probability
                if self.p > 0:
                    new_dist = {}
                    for k, p in self.dist.items():
                        new_dist[k+1] = new_dist.get(k+1, 0.0) + p * self.p
                        new_dist[k] = new_dist.get(k, 0.0) + p * (1 - self.p)
                    self.dist = new_dist
                    self.maxv += 1

        # Build interval tree
        segs = [Segment(1, n, 0.0)] + [Segment(l, r, p) for l, r, p in recommendations]
        segs.sort(key=lambda x: (x.a, -(x.b - x.a)))

        # Build hierarchy
        stack = [segs[0]]
        for s in segs[1:]:
            while stack and not (stack[-1].a <= s.a and s.b <= stack[-1].b):
                stack.pop()
            if stack:
                stack[-1].children.append(s)
            stack.append(s)

        # Solve root
        segs[0].solve(a)
        expectation = sum(k * p for k, p in segs[0].dist.items())
        return expectation
