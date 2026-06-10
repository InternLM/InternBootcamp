import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class EandreachabilityInstructionGenerator(BaseInstructionGenerator):
    """Eandreachability Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_q=3, max_val=300000):
        """
        初始化Eandreachability指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(2, self.max_n)
        q = random.randint(1, self.max_q)
        a = [random.randint(0, self.max_val) for _ in range(n)]
        queries = []
        for _ in range(q):
            x = random.randint(1, n-1)
            y = random.randint(x+1, n)
            queries.append((x, y))
        
        correct_answers = self.calculate_answers(a, queries)
        return {
            'n': n,
            'q': q,
            'a': a,
            'queries': queries,
            'correct_answers': correct_answers
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        queries = question_case['queries']
        problem_text = (
            "Toad Pimple有一个整数数组：[" + ", ".join(map(str, a)) + "]\n"
            "共有" + str(len(queries)) + "个查询需要判断可达性。\n"
            "规则说明：\n"
            "1. y可从x到达的条件：存在下标序列x = p₁ < p₂ < ... < pₖ = y，且每对相邻元素的按位与结果大于0\n"
            "2. 若目标元素值为0则直接不可达\n"
            "需要判断的查询对（x, y）：\n" +
            "\n".join([f"查询{i+1}: {x} → {y}" for i, (x, y) in enumerate(queries)]) +
            "\n请逐行输出'Shi'或'Fou'，并将答案包裹在[answer]标签内。例如：\n"
            "[answer]\nShi\nFou\n[/answer]"
        )
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def calculate_answers(self, a, queries):
        n = len(a)
        a_ext = [0] + a  # 1-based
        nodes = [{'next': [0]*19} for _ in range(n+2)]  # 1-based

        # Initialize ns structure
        ns = [[[] for _ in range(19)] for _ in range(19)]

        for i in range(1, n+1):
            ai = a_ext[i]
            has_bits = []
            want_bits = []
            for bit in range(19):
                if (ai >> bit) & 1:
                    has_bits.append(bit)
                    nodes[i]['next'][bit] = i
                else:
                    want_bits.append(bit)

            # Process connections for existing bits
            for h1 in has_bits:
                for h2 in has_bits:
                    while ns[h1][h2]:
                        v = ns[h1][h2].pop()
                        if nodes[v]['next'][h2] == 0 or nodes[v]['next'][h2] > i:
                            nodes[v]['next'][h2] = i
                            for b in range(19):
                                if nodes[v]['next'][b] == 0:
                                    ns[h2][b].append(v)

            # Add to want bits' ns
            for h in has_bits:
                for w in want_bits:
                    ns[h][w].append(i)

        # Process queries
        results = []
        for x, y in queries:
            if a_ext[y] == 0:
                results.append('Fou')
                continue

            reachable = False
            for bit in range(19):
                if (a_ext[y] >> bit) & 1:
                    if nodes[x]['next'][bit] != 0 and nodes[x]['next'][bit] <= y:
                        reachable = True
                        break
            results.append('Shi' if reachable else 'Fou')
        return results
