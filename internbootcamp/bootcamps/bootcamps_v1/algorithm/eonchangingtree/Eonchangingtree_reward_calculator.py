import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class EonchangingtreeRewardCalculator(BaseRewardCalculator):
    """Eonchangingtree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        try:
            return [int(m) % mod for m in matches] if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = [q['expected'] for q in identity['queries'] if q['type'] == 2]
        return solution == expected if solution else False
    
    # 其他额外方法

