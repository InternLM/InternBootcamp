import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def solve_puzzle(names):
    graph = defaultdict(list)
    for c in string.ascii_lowercase:  # 初始化所有字母节点
        graph[c] = []
    
    # 构建字母约束关系图
    for i in range(len(names)-1):
        a, b = names[i], names[i+1]
        min_len = min(len(a), len(b))
        j = 0
        while j < min_len and a[j] == b[j]:
            j += 1
        
        if j == min_len:  # 处理前缀情况
            if len(a) > len(b):
                return "Impossible"
            continue
        
        # 添加字符顺序约束：a[j]必须出现在b[j]之前
        x, y = a[j], b[j]
        graph[y].append(x)  # 修正方向：y依赖x → x必须出现在y前面
    
    # 拓扑排序
    in_degree = {c:0 for c in string.ascii_lowercase}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    
    queue = deque([c for c in string.ascii_lowercase if in_degree[c] == 0])
    top_order = []
    
    while queue:
        u = queue.popleft()
        top_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    return "Impossible" if len(top_order)!=26 else "".join(reversed(top_order))


class CfoxandnamesRewardCalculator(BaseRewardCalculator):
    """Cfoxandnames奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL|re.IGNORECASE)
        if not matches:
            return None
        ans = matches[-1].strip().lower()
        return ans if ans == "impossible" or len(ans)==26 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        names = identity['names']
        
        if solution == "impossible":
            return solve_puzzle(names) == "Impossible"
        
        if len(solution)!=26 or len(set(solution))!=26:
            return False
        
        order = {c:i for i,c in enumerate(solution)}
        for i in range(len(names)-1):
            a, b = names[i], names[i+1]
            found = False
            for j in range(min(len(a), len(b))):
                if a[j] != b[j]:
                    if order[a[j]] > order[b[j]]:
                        return False
                    found = True
                    break
            if not found and len(a) > len(b):
                return False
        return True
    
    # 其他额外方法

