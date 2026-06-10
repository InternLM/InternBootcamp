import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class StitchesRewardCalculator(BaseRewardCalculator):
    """Stitches奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        import ast
        # Find last answer block
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_answer)
            if not isinstance(solution, list):
                return None
            for stitch in solution:
                if len(stitch) != 2 or not all(isinstance(p, tuple) and len(p)==2 for p in stitch):
                    return None
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            rows = identity['rows']
            cols = identity['cols']
            numbered_cells = {(c['x'], c['y']): c['num'] for c in identity['numbered_cells']}
            
            # 验证基本结构
            stitches = set()
            for stitch in solution:
                # 验证缝线格式
                if len(stitch) != 2:
                    return False
                p1, p2 = stitch
                if not (isinstance(p1, tuple) and isinstance(p2, tuple) and len(p1)==2 and len(p2)==2):
                    return False
                x1, y1 = p1
                x2, y2 = p2
                # 验证坐标有效性
                if not (0 <= x1 < rows and 0 <= y1 < cols and 0 <= x2 < rows and 0 <= y2 < cols):
                    return False
                # 验证相邻性
                dx = abs(x1 - x2)
                dy = abs(y1 - y2)
                if not ((dx == 1 and dy == 0) or (dy == 1 and dx == 0)):
                    return False
                # 标准化缝线存储
                stitches.add(frozenset({p1, p2}))
            
            # 构建邻接表
            graph = defaultdict(list)
            for s in stitches:
                p1, p2 = s
                graph[p1].append(p2)
                graph[p2].append(p1)
            
            # 检查数字点约束
            for (x, y), num in numbered_cells.items():
                actual = len(graph.get((x, y), []))
                if actual != num:
                    return False
            
            # 检查所有节点的度数
            visited = set()
            for node in graph:
                # 处理未访问节点
                if node in visited:
                    continue
                # 检查是否为合法环结构
                current = node
                prev = None
                path = []
                while True:
                    next_nodes = [n for n in graph[current] if n != prev]
                    if len(next_nodes) != 1:
                        break  # 分支或末端
                    prev, current = current, next_nodes[0]
                    if current == node:  # 闭环检查
                        break
                    path.append(current)
                    if current in visited:
                        return False
                    visited.add(current)
                # 验证是否形成闭环
                if current != node or len(graph[node]) != 2:
                    return False
            
            # 检查未编号点度数
            for node in graph:
                if node not in numbered_cells:
                    if len(graph[node]) not in (0, 2):
                        return False
            
            # 检查单一环
            # 确保所有连接点被访问且构成单个环
            component = []
            stack = []
            if graph:
                start = next(iter(graph))
                stack.append(start)
                visited_nodes = set()
                while stack:
                    node = stack.pop()
                    if node in visited_nodes:
                        continue
                    visited_nodes.add(node)
                    for neighbor in graph[node]:
                        if neighbor not in visited_nodes:
                            stack.append(neighbor)
                if len(visited_nodes) != len(graph):
                    return False
            return True
        except:
            return False
    
    # 其他额外方法

