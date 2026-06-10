import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CfoxandnamesInstructionGenerator(BaseInstructionGenerator):
    """Cfoxandnames Bootcamp指令生成器"""
    
    def __init__(self, min_names=1, max_names=10, min_length=1, max_length=10, valid_ratio=0.5):
        """
        初始化Cfoxandnames指令生成器
        
        Args:
            min_names: 参数描述
            max_names: 参数描述
            min_length: 参数描述
            max_length: 参数描述
            valid_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_names = min_names
        self.max_names = max_names
        self.min_length = min_length
        self.max_length = max_length
        self.valid_ratio = valid_ratio
    
    def case_generator(self):
        for _ in range(1000):  # 增加尝试次数
            n = random.randint(self.min_names, self.max_names)
            names = self._generate_names(n)
            solution = solve_puzzle(names)
            
            # 动态调整有效案例生成概率
            target_valid = random.random() < self.valid_ratio
            if (solution != "Impossible") == target_valid:
                return {'names': names}
        
        # 回退案例：生成保证有效的案例
        return {'names': sorted(["a"*i for i in range(1,4)], key=lambda x: (-len(x), x))}
    
    @staticmethod
    def prompt_func(question_case):
        names = question_case['names']
        problem = (
            "Determine if a custom alphabet exists to make the names lex ordered.\n"
            f"Input:\n{len(names)}\n" + "\n".join(names) + "\n\n"
            "Output format: [answer]<LETTER_ORDER|Impossible>[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_names(self, n):
        names = set()
        char_pool = random.sample(string.ascii_lowercase, random.randint(3,5))  # 限制字符集增加冲突

        while len(names) < n:
            length = random.randint(self.min_length, self.max_length)
            name = "".join(random.choices(char_pool, k=length))
            names.add(name)
        return list(names)
