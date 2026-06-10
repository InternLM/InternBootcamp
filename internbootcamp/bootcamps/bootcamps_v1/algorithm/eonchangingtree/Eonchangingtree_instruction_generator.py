import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

mod = 10**9 + 7



# === 源文件中的全局函数 ===

def build_adj(parents, n):
    adj = {i: [] for i in range(1, n+1)}
    for i in range(2, n+1):
        parent = parents[i-2]
        adj[parent].append(i)
    return adj

def dfs(x, parent_adj, tin, tout, dep, current_time, current_g):
    current_time[0] += 1
    tin[x] = current_time[0]
    dep[tin[x]] = current_g
    for child in parent_adj.get(x, []):
        dfs(child, parent_adj, tin, tout, dep, current_time, current_g-1)
    tout[x] = current_time[0]

def perform_dfs(n, parent_adj):
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    dep = [0] * (n + 2)  # tin values are 1-based
    current_time = [0]
    dfs(1, parent_adj, tin, tout, dep, current_time, n)
    return tin, tout, dep

def process_queries_for_identity(queries, n, tin_dict, tout_dict, dep_list):
    a = [0] * (n + 2)
    b = [0] * (n + 2)
    expected_outputs = []
    for query in queries:
        if query['type'] == 1:
            v = query['v']
            x = query['x']
            k = query['k']
            tin_v = tin_dict[v]
            tout_v = tout_dict[v]
            f1 = (x - dep_list[tin_v] * k) % mod
            f2 = k % mod
            for u in range(1, n+1):
                u_tin = tin_dict[u]
                if tin_v <= u_tin <= tout_v:
                    a[u_tin] = (a[u_tin] + f1) % mod
                    b[u_tin] = (b[u_tin] + f2) % mod
        else:
            v = query['v']
            u_tin = tin_dict[v]
            res = (a[u_tin] + b[u_tin] * dep_list[u_tin]) % mod
            expected_outputs.append(res)
    return expected_outputs


class EonchangingtreeInstructionGenerator(BaseInstructionGenerator):
    """Eonchangingtree Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_q=5):
        """
        初始化Eonchangingtree指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        parents = []
        if n > 1:
            parents = [random.randint(1, i-1) for i in range(2, n+1)]
        adj = build_adj(parents, n)
        tin, tout, dep = perform_dfs(n, adj)
        tin_dict = {x: tin[x] for x in range(1, n+1)}
        tout_dict = {x: tout[x] for x in range(1, n+1)}
        q = random.randint(1, self.max_q)
        queries = []
        for _ in range(q):
            if random.random() < 0.3 or not any(q.get('type') == 2 for q in queries):
                v = random.randint(1, n)
                queries.append({'type': 2, 'v': v})
            else:
                v = random.randint(1, n)
                x = random.randint(0, mod-1)
                k = random.randint(0, mod-1)
                queries.append({'type': 1, 'v': v, 'x': x, 'k': k})
        expected_outputs = process_queries_for_identity(queries, n, tin_dict, tout_dict, dep)
        new_queries = []
        output_idx = 0
        for q in queries:
            if q['type'] == 2:
                new_q = q.copy()
                new_q['expected'] = expected_outputs[output_idx]
                new_queries.append(new_q)
                output_idx += 1
            else:
                new_queries.append(q)
        return {
            'n': n,
            'parents': parents,
            'queries': new_queries,
            'tin_dict': tin_dict,
            'tout_dict': tout_dict,
            'dep_list': dep
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [
            str(question_case['n']),
            ' '.join(map(str, question_case['parents'])) if question_case['n'] > 1 else '',
            str(len(question_case['queries']))
        ]
        for q in question_case['queries']:
            if q['type'] == 1:
                input_lines.append(f"1 {q['v']} {q['x']} {q['k']}")
            else:
                input_lines.append(f"2 {q['v']}")
        input_str = '\n'.join(input_lines)
        return f"""你正在解决一个树处理问题。处理所有查询并将每个类型2的答案放在[answer]和[/answer]之间。输入数据如下：

{input_str}

规则：
1. 类型1查询为节点v及其后代按距离加值。
2. 类型2查询输出节点值模10^9+7的结果。

答案格式示例：
[answer]结果1[/answer]
[answer]结果2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

