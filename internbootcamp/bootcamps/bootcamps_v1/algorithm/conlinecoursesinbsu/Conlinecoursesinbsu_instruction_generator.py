import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class ConlinecoursesinbsuInstructionGenerator(BaseInstructionGenerator):
    """Conlinecoursesinbsu Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10, cycle_prob=0.3):
        """
        初始化Conlinecoursesinbsu指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            cycle_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.cycle_prob = cycle_prob  # 生成循环依赖的概率
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        k = random.randint(1, n)
        courses = list(range(1, n+1))
        random.shuffle(courses)
        main_courses = random.sample(courses, k)
        
        # 生成课程依赖关系
        dependencies = {}
        for course in courses:
            if random.random() < self.cycle_prob:
                # 允许生成任意依赖（可能产生循环）
                ti = random.randint(0, n-1)
                possible_deps = [c for c in courses if c != course]
                deps = random.sample(possible_deps, ti) if possible_deps else []
            else:
                # 生成无环依赖
                idx = courses.index(course)
                possible_deps = courses[:idx]
                ti = random.randint(0, len(possible_deps))
                deps = random.sample(possible_deps, ti) if possible_deps else []
            dependencies[course] = {'ti': len(deps), 'deps': deps}

        # 构建必须课程集合和邻接表
        required = set()
        q = deque(main_courses)
        while q:
            c = q.popleft()
            if c not in required:
                required.add(c)
                for dep in dependencies[c]['deps']:
                    q.append(dep)

        adj = {}
        for course in required:
            adj[course] = []
            for dep in dependencies[course]['deps']:
                if dep in required:
                    adj[course].append(dep)

        has_cycle = self.detect_cycle(adj)
        
        # 构建正确解（如果不存在循环）
        correct_order = []
        if not has_cycle:
            in_degree = {course: 0 for course in adj}
            for course in adj:
                for dep in adj[course]:
                    in_degree[dep] += 1
            q = deque([c for c in adj if in_degree[c] == 0])
            while q:
                node = q.popleft()
                correct_order.append(node)
                for neighbor in adj[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        q.append(neighbor)
            correct_order = list(reversed(correct_order))  # 调整拓扑顺序为执行顺序

        return {
            'n': n,
            'k': k,
            'main': main_courses,
            'dependencies': [{'course': c, 'ti': dependencies[c]['ti'], 'deps': dependencies[c]['deps']} for c in courses],
            'possible': not has_cycle,
            'correct_order': correct_order if not has_cycle else None
        }
    
    @staticmethod
    def prompt_func(question_case):
        main = ' '.join(map(str, question_case['main']))
        desc = f"""你是贝兰德国立大学的学生，需要完成专业中的{question_case['k']}门主修课程。总共有{question_case['n']}门课程，存在以下依赖关系：
        
课程编号 | 前置课程数量 | 前置课程列表
--------|------------|------------
"""
        for dep in question_case['dependencies']:
            desc += f"{dep['course']} | {dep['ti']} | {' '.join(map(str, dep['deps'])) if dep['deps'] else '无'}\n"
        
        desc += """
请确定完成所有主修课程需要的最少课程数量，并给出正确学习顺序。如果存在循环依赖无法完成，请输出-1。

答案格式要求：
- 如果无解：\n[answer]\n-1\n[/answer]
- 如果有解：\n[answer]\n<m>\n<course sequence>\n[/answer]
例如：
[answer]
3
1 2 3
[/answer]"""
        return desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def detect_cycle(self, adj):
        visited = {}
        stack = set()

        def dfs(node):
            if node in stack:
                return True
            if node in visited:
                return False
            visited[node] = True
            stack.add(node)
            for neighbor in adj.get(node, []):
                if dfs(neighbor):
                    return True
            stack.remove(node)
            return False

        for node in adj:
            if node not in visited:
                if dfs(node):
                    return True
        return False
