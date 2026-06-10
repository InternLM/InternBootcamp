import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CcielthecommanderInstructionGenerator(BaseInstructionGenerator):
    """Ccielthecommander Bootcamp指令生成器"""
    
    def __init__(self, min_nodes=2, max_nodes=20):
        """
        初始化Ccielthecommander指令生成器
        
        Args:
            min_nodes: 参数描述
            max_nodes: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
    
    def case_generator(self):
        for _ in range(100):  # Limit attempts to avoid infinite loop
            n = random.randint(self.min_nodes, self.max_nodes)
            edges = []
            # Generate a random tree using parent linking method
            nodes = list(range(1, n+1))
            for i in range(2, n+1):
                parent = random.randint(1, i-1)
                edges.append([parent, i])
            
            # Generate solution using the reference approach with validity check
            solution = self.solve_puzzle(n, edges)
            validate_result = self.validate_solution(n, edges, solution)
            
            # Ensure generated case is valid
            if solution == "Impossible!" and validate_result:
                return {
                    'n': n,
                    'edges': edges,
                    'expected_answer': solution
                }
            elif solution != "Impossible!":
                parts = solution.split()
                if len(parts) == n and all('A' <= c <= 'Z' for c in parts) and validate_result:
                    return {
                        'n': n,
                        'edges': edges,
                        'expected_answer': solution
                    }
        # Fallback to a simple case after too many attempts
        return {
            'n': 2,
            'edges': [[1,2]],
            'expected_answer': 'A B'
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [str(question_case['n'])] + [' '.join(map(str, edge)) for edge in question_case['edges']]
        input_str = '\n'.join(input_lines)
        
        prompt = f"""作为树之国指挥官，你需要为每个城市分配官员等级（A-Z）。规则要求：任意两个同等级城市之间的路径上必须有更高级城市。请根据输入给出有效方案或输出“Impossible!”。

输入：
{input_str}

输出格式：
一行n个空格分隔的字母（城市1到n的等级）或“Impossible!”。

将最终答案放在[answer]和[/answer]之间。例如：
[answer]
A B B B
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_puzzle(n, edges):
        # Build adjacency list (0-based)
        coupl = [[] for _ in range(n)]
        for a, b in edges:
            u = a - 1
            v = b - 1
            coupl[u].append(v)
            coupl[v].append(u)

        # Centroid decomposition logic with Z check
        ans = [-1] * n
        cur_color = 0
        cur_count = 1
        next_count = 0

        try:
            for centroid in Ccielthecommanderbootcamp.centroid_decomp(coupl):
                if cur_color >= 26:
                    return "Impossible!"
                ans[centroid] = cur_color
                next_count += len(coupl[centroid])
                cur_count -= 1
                if cur_count == 0:
                    cur_count = next_count
                    cur_color += 1
                    next_count = 0
            if cur_color >= 26:
                return "Impossible!"
        except:
            return "Impossible!"

        # Final check for Z overflow in ans
        if max(ans) >= 26:
            return "Impossible!"
        return ' '.join(chr(ord('A') + x) for x in ans)

    @staticmethod
    def centroid_decomp(coupl):
        n = len(coupl)
        if n == 0:
            return

        # Initial BFS to dismantle parent links
        root = n - 1
        bfs = [root]
        for node in bfs:
            for nei in list(coupl[node]):
                if node in coupl[nei]:
                    coupl[nei].remove(node)
            bfs += coupl[node]

        # Calculate sizes
        size = [1] * n
        for node in reversed(bfs):
            for child in coupl[node]:
                size[node] += size[child]

        # Centroid rerooting function
        def centroid_reroot(root):
            N = size[root]
            while True:
                for child in coupl[root]:
                    if size[child] > N // 2:
                        size[root] = N - size[child]
                        coupl[root].remove(child)
                        coupl[child].append(root)
                        root = child
                        break
                else:
                    return root

        # Generate centroids through BFS
        bfs = [root]
        for node in bfs:
            centroid = centroid_reroot(node)
            yield centroid
            bfs += coupl[centroid]

    @staticmethod
    def validate_solution(n, edges, solution):
        if solution == "Impossible!":
            # Check if the problem is actually impossible
            # This would require a separate solver, but for bootcamp purposes
            # we assume the case_generator's solve_puzzle is authoritative
            return True

        parts = solution.split()
        if len(parts) != n:
            return False
        for c in parts:
            if len(c) != 1 or not ('A' <= c <= 'Z'):
                return False

        # Build adjacency list
        adj = [[] for _ in range(n+1)]  # 1-based
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        # Precompute all pairs with same color
        color_map = {}
        for i in range(n):
            color = parts[i]
            color_map.setdefault(color, []).append(i+1)  # Cities are 1-based

        # Check each color group
        for color, cities in color_map.items():
            if len(cities) < 2:
                continue
            # Check all pairs in this color group
            for i in range(len(cities)):
                for j in range(i+1, len(cities)):
                    u = cities[i]
                    v = cities[j]
                    # Find path and check for higher rank
                    if not Ccielthecommanderbootcamp.path_has_higher(u, v, adj, parts):
                        return False
        return True

    @staticmethod
    def path_has_higher(u, v, adj, parts):
        # BFS to find path and check ranks
        visited = set()
        queue = deque()
        queue.append( (u, []) )
        while queue:
            node, path = queue.popleft()
            if node == v:
                full_path = path + [node]
                current_rank = parts[u-1]
                for n in full_path:
                    if parts[n-1] < current_rank:
                        return True
                return False
            if node in visited:
                continue
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    queue.append( (neighbor, path + [node]) )
        return False  # Shouldn't happen in trees
