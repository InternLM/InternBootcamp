import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_correct_output(n, m, edges, updates):
    G = [[] for _ in range(n + 1)]
    for a, b in edges:
        G[a].append(b)
        G[b].append(a)
    
    arr = list(range(n + 1))
    deg = [len(g) for g in G]
    gtrs = [[] for _ in range(n + 1)]
    cnt = [0] * (n + 1)
    
    ans = 0
    for u in range(1, n + 1):
        if deg[u] > 320:
            gtrs[u] = [v for v in G[u] if arr[v] > arr[u]]
            ans += (deg[u] - len(gtrs[u])) * len(gtrs[u])
        else:
            cnt[u] = sum(1 for v in G[u] if arr[v] > arr[u])
            ans += (deg[u] - cnt[u]) * cnt[u]
    
    correct_outputs = [ans]
    q = len(updates)
    
    for t in range(1, q + 1):
        u = updates[t - 1]
        ans -= (deg[u] - (len(gtrs[u]) if deg[u] > 320 else cnt[u])) * (len(gtrs[u]) if deg[u] > 320 else cnt[u])
        
        candidates = gtrs[u] if deg[u] > 320 else G[u]
        processed = [v for v in candidates if arr[u] < arr[v]]
        
        for v in processed:
            ans_before = (deg[v] - (len(gtrs[v]) if deg[v] > 320 else cnt[v])) * (len(gtrs[v]) if deg[v] > 320 else cnt[v])
            if deg[v] > 320:
                gtrs[v].append(u)
            else:
                cnt[v] += 1
            ans_after = (deg[v] - (len(gtrs[v]) if deg[v] > 320 else cnt[v])) * (len(gtrs[v]) if deg[v] > 320 else cnt[v])
            ans += (ans_after - ans_before)
        
        if deg[u] > 320:
            gtrs[u].clear()
        else:
            cnt[u] = 0
        
        arr[u] = n + t
        correct_outputs.append(ans)
    
    return correct_outputs


class DkonradandcompanyevaluationInstructionGenerator(BaseInstructionGenerator):
    """Dkonradandcompanyevaluation Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=20, max_q=5):
        """
        初始化Dkonradandcompanyevaluation指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)  # 确保最小n=1
        self.max_m = max_m
        self.max_q = max_q
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        max_possible_m = n * (n - 1) // 2
        m = random.randint(0, min(self.max_m, max_possible_m))
        
        edges_set = set()
        available_pairs = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1)] if n >= 2 else []
        if available_pairs and m > 0:
            edges_set.update(random.sample(available_pairs, k=min(m, len(available_pairs))))
        
        edges = [list(pair) for pair in edges_set]
        q = random.randint(0, self.max_q)
        updates = [random.randint(1, n) for _ in range(q)]
        
        correct_outputs = compute_correct_output(n, m, edges, updates)
        
        return {
            'n': n,
            'm': m,
            'edges': edges,
            'q': q,
            'updates': updates,
            'correct_outputs': correct_outputs
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['m']}"]
        input_lines.extend(f"{a} {b}" for a, b in question_case['edges'])
        input_lines.append(str(question_case['q']))
        input_lines.extend(map(str, question_case['updates']))
        input_str = '\n'.join(input_lines)
        
        prompt = f"""Konrad needs to calculate dangerous triples in VoltModder. A dangerous triple is a sequence of three employees a->b->c where a dislikes b, b dislikes c, and salaries satisfy a > b > c. Each day an employee's salary is updated to be the highest. Output the number of dangerous triples before each day.

Input format:
n m
a1 b1
...
am bm
q
v1
...
vq

Output q+1 integers. Put your answer between [answer] and [/answer]. Example:
[answer]
0
1
2
[/answer]

Current Input:
{input_str}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

