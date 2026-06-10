import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class CcandiesdistributionInstructionGenerator(BaseInstructionGenerator):
    """Ccandiesdistribution Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=15):
        """
        初始化Ccandiesdistribution指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        case_type = random.choice([
            'valid_standard', 
            'valid_duplicates',
            'invalid_boundary',
            'invalid_overflow',
            'invalid_sum'
        ])
        
        if case_type.startswith('valid'):
            return self.generate_valid_case(case_type)
        return self.generate_invalid_case(case_type)
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        def format_array(arr):
            return ' '.join(f'\033[34m{a}\033[0m' for a in arr)  # 使用ANSI颜色增强显示
        
        return f"""## 幼儿园糖果分配验证问题（难度：★★★☆☆）

### 问题描述
幼儿园老师记录了{n}个孩子的糖果分配观察结果，但不确定孩子们是否计算正确。每个孩子i报告了两个数值：
- l_i（左侧糖果数比自己多的人数）：{format_array(question_case['l'])}
- r_i（右侧糖果数比自己多的人数）：{format_array(question_case['r'])}

### 验证要求
1. 判断是否存在满足以下条件的糖果分配方案：
   - 每个孩子获得1~{n}颗糖果
   - 每个孩子的l_i和r_i计算准确
2. 若存在，给出任意可行方案；否则说明无解

### 输出格式
将最终答案用[answer]标签包裹，示例如下：
[answer]
YES
2 3 1 2
[/answer]
或
[answer]
NO
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        a = []

        # 生成策略优化
        if case_type == 'valid_standard':
            # 使用拓扑排序生成合法案例
            graph = [[] for _ in range(n)]
            in_degree = [0]*n
            q = deque()

            # 构造约束关系
            for i in range(n):
                for j in range(i+1, n):
                    if random.random() < 0.3:
                        graph[i].append(j)
                        in_degree[j] += 1
                    else:
                        graph[j].append(i) 
                        in_degree[i] += 1

            # 拓扑排序生成合法值
            while q:
                u = q.popleft()
                a.append(random.randint(1, n))
                for v in graph[u]:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        q.append(v)
            a += [random.randint(1, n) for _ in range(n - len(a))]
        else:  # valid_duplicates
            base = random.randint(1, n//2)
            a = [base + i % 3 for i in range(n)]
            random.shuffle(a)

        # 计算合法约束
        l = [sum(a[j] > a[i] for j in range(i)) for i in range(n)]
        r = [sum(a[j] > a[i] for j in range(i+1, n)) for i in range(n)]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': True,
            'type': case_type
        }

    def generate_invalid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        l = [0]*n
        r = [0]*n

        if case_type == 'invalid_boundary':
            # 边界条件无效：首位儿童左边有人，末位儿童右边有人
            targets = [0, n-1] if n > 1 else [0]
            for i in targets:
                if i == 0:
                    l[i] = random.randint(1, 3)
                else:
                    r[i] = random.randint(1, 3)

        elif case_type == 'invalid_overflow':
            # 数值超限：单个值超过理论最大值
            i = random.randint(0, n-1)
            max_possible = i if i < n-1 else 0
            l[i] = max_possible + random.randint(1, 2)

        elif case_type == 'invalid_sum':
            # 总和矛盾：l_i + r_i > 可能的最大值
            i = random.randint(0, n-1)
            max_total = (n - 1) - (i + (n - i - 1))
            if max_total < 0: max_total = 0
            current_sum = random.randint(max_total + 1, max_total + 3)
            l[i] = current_sum // 2
            r[i] = current_sum - l[i]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': False,
            'type': case_type
        }
