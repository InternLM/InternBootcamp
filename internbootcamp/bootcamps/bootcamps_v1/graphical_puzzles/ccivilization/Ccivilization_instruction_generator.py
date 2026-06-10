import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcivilizationInstructionGenerator(BaseInstructionGenerator):
    """Ccivilization Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ccivilization指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.params = {
            'n': params.get('n', 6),
            'm': params.get('m', 0),
            'q': params.get('q', 6),
            'max_retries': 10  # 用于生成道路时的重试次数
        }
    
    def case_generator(self):
        n = self.params['n']
        m = self.params['m']
        q = self.params['q']
        max_retries = self.params['max_retries']
        
        parent = list(range(n + 1))  # 1-based indexing
        diameter = [0] * (n + 1)
        
        # 生成 m 条道路，确保形成树结构
        roads = []
        for _ in range(m):
            added = False
            retries = 0
            while not added and retries < max_retries:
                a = random.randint(1, n)
                b = random.randint(1, n)
                if a == b:
                    continue
                root_a = self.find(parent, a)
                root_b = self.find(parent, b)
                if root_a != root_b:
                    roads.append((a, b))
                    # 计算新直径
                    t1_a = diameter[root_a] // 2
                    t2_a = diameter[root_a] - t1_a
                    t1_b = diameter[root_b] // 2
                    t2_b = diameter[root_b] - t1_b
                    new_diam = max(diameter[root_a], diameter[root_b], t2_a + t2_b + 1)
                    # 合并区域
                    if diameter[root_a] > diameter[root_b]:
                        root_a, root_b = root_b, root_a
                    parent[root_a] = root_b
                    diameter[root_b] = new_diam
                    added = True
                retries += 1
        
        # 生成 q 个查询
        queries = []
        results = []
        for _ in range(q):
            op = random.choice([1, 2])
            if op == 1:
                x = random.randint(1, n)
                root = self.find(parent, x)
                current_diam = diameter[root]
                queries.append(('1', x))
                results.append(current_diam)
            else:
                x = random.randint(1, n)
                y = random.randint(1, n)
                queries.append(('2', x, y))
                root_x = self.find(parent, x)
                root_y = self.find(parent, y)
                if root_x != root_y:
                    if diameter[root_x] > diameter[root_y]:
                        root_x, root_y = root_y, root_x
                    t1 = diameter[root_x] // 2
                    t2 = diameter[root_x] - t1
                    t3 = diameter[root_y] // 2
                    t4 = diameter[root_y] - t3
                    new_diam = max(diameter[root_x], diameter[root_y], t2 + t4 + 1)
                    parent[root_x] = root_y
                    diameter[root_y] = new_diam
        
        case = {
            'n': n,
            'm': m,
            'q': q,
            'roads': roads,
            'queries': queries,
            'results': results
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        q = question_case['q']
        roads = question_case['roads']
        queries = question_case['queries']
        
        road_descriptions = []
        for a, b in roads:
            road_descriptions.append("城市 {} 和 {} 之间有一条道路。".format(a, b))
        
        query_descriptions = []
        for i, query in enumerate(queries, 1):
            if query[0] == '1':
                query_descriptions.append("{}. 查询城市 {} 所在区域的最长路径长度。".format(i, query[1]))
            else:
                query_descriptions.append("{}. 合并城市 {} 和 {} 所在的区域。".format(i, query[1], query[2]))
        
        prompt = (
            "游戏开始时有 {} 个城市，其中 {} 条道路。道路情况如下：\n"
            "{}\n"
            "\n接下来有 {} 个查询：\n"
            "{}\n"
            "\n对于每个类型1的查询，请输出该区域的最长路径长度。请将所有类型1查询的结果按顺序用逗号分隔，并放在 [answer] 标签中。例如：[answer]4,5,6[/answer]\n"
            "\n请详细解答每个查询，并将所有类型1查询的结果放在上述格式中。"
        ).format(
            n, m, '\n'.join(road_descriptions),
            q, '\n'.join(query_descriptions)
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def find(parent, x):
        if parent[x] != x:
            parent[x] = Ccivilizationbootcamp.find(parent, parent[x])
        return parent[x]
