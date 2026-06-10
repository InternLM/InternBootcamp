import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
import re
from typing import List
from typing import Dict
from typing import Any
from collections import defaultdict




class CilyaandthetreeInstructionGenerator(BaseInstructionGenerator):
    """Cilyaandthetree Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_a=100, **kwargs):
        """
        初始化Cilyaandthetree指令生成器
        
        Args:
            max_n: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
        self.max_a = max_a
    
    def case_generator(self) -> Dict[str, Any]:
        """生成有效树结构并计算正确解"""
        n = random.randint(1, self.max_n)
        a = [random.randint(1, self.max_a) for _ in range(n)]
        edges = self._generate_valid_tree(n)
        correct_output = self._compute_solution(n, a, edges)
        
        return {
            'n': n,
            'a': a,
            'edges': edges,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        problem = (
            "给定根在顶点1的树，每个顶点有整数a_i。定义顶点x的美丽值为根到x路径上的所有数的GCD。"
            "允许将任意一个节点的值改为0或保持不变。对每个顶点求可能的最大美丽值。\n\n"
            f"输入格式：\n第一行：n={case['n']}\n第二行：{' '.join(map(str, case['a']))}\n"
            "接下来的n-1行每行两个整数描述边：\n" + 
            '\n'.join(f"{x} {y}" for x, y in case['edges']) + 
            "\n\n请输出n个用空格分隔的整数，将答案放在[answer]和[/answer]之间。"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_tree(self, n: int) -> List[List[int]]:
        """生成以1为根的合法树结构"""
        if n == 1:
            return []

        nodes = list(range(2, n+1))
        random.shuffle(nodes)
        edges = []
        connected = {1}
        for node in nodes:
            parent = random.choice(list(connected))
            edges.append([parent, node])
            connected.add(node)
        return edges

    def _compute_solution(self, n: int, a: List[int], edges: List[List[int]]) -> List[int]:
        """正确实现参考算法逻辑"""
        # 构建邻接表（1-based）
        adj = defaultdict(list)
        for x, y in edges:
            adj[x].append(y)
            adj[y].append(x)

        # 初始化数据结构
        res = [0] * (n+1)  # 1-based索引
        res[1] = a[0]
        cnt = defaultdict(int)
        max_depth = defaultdict(int)

        # 预计算根节点所有因数
        root_val = a[0]
        divisors = set()
        d = 1
        while d*d <= root_val:
            if root_val % d == 0:
                divisors.add(d)
                if d != root_val//d:
                    divisors.add(root_val//d)
            d += 1

        # 初始化因数计数
        for d in divisors:
            cnt[d] = 1

        # DFS遍历
        stack = [(1, 0, root_val)]  # (current, parent, current_gcd)
        path = []

        while stack:
            node, parent, current_gcd = stack.pop()
            path.append(node)

            # 计算当前路径长度
            current_depth = len(path)

            # 计算当前节点的可能最大值
            max_val = current_gcd
            for d in sorted(divisors, reverse=True):
                if cnt[d] >= current_depth - 1:
                    max_val = max(max_val, d)
                    break

            res[node] = max_val

            # 处理子节点
            for child in adj[node]:
                if child == parent:
                    continue

                # 计算子节点的GCD
                child_gcd = math.gcd(current_gcd, a[child-1])

                # 更新因数计数
                for d in divisors:
                    if a[child-1] % d == 0:
                        cnt[d] += 1

                stack.append((child, node, child_gcd))

            # 回溯时恢复计数
            if path:
                last_node = path.pop()
                for d in divisors:
                    if a[last_node-1] % d == 0:
                        cnt[d] = max(cnt[d]-1, 0)

        return [res[i] for i in range(1, n+1)]
