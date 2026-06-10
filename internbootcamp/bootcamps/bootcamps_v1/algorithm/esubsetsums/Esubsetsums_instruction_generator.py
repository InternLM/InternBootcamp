import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EsubsetsumsInstructionGenerator(BaseInstructionGenerator):
    """Esubsetsums Bootcamp指令生成器"""
    
    def __init__(self, n_max=5, m_max=3, q_max=5, max_element=10, min_element=-10, set_size_min=1, set_size_max=5, query_prob=0.3):
        """
        初始化Esubsetsums指令生成器
        
        Args:
            n_max: 参数描述
            m_max: 参数描述
            q_max: 参数描述
            max_element: 参数描述
            min_element: 参数描述
            set_size_min: 参数描述
            set_size_max: 参数描述
            query_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_max = n_max
        self.m_max = m_max
        self.q_max = q_max
        self.max_element = max_element
        self.min_element = min_element
        self.set_size_min = set_size_min
        self.set_size_max = set_size_max
        self.query_prob = query_prob
    
    def case_generator(self):
        while True:  # 新增循环确保至少一个查询输出
            n = random.randint(1, self.n_max)
            m = random.randint(1, self.m_max)
            q = random.randint(1, self.q_max)
            
            a = [random.randint(self.min_element, self.max_element) for _ in range(n)]
            
            sets = []
            for _ in range(m):
                max_possible = min(n, self.set_size_max)
                k = random.randint(max(1, self.set_size_min), max_possible)
                available = list(range(1, n+1))
                random.shuffle(available)
                sets.append(sorted(available[:k]))
            
            queries = []
            current_a = a.copy()
            correct_outputs = []
            has_query = False  # 新增验证标记
            
            for _ in range(q):
                if not has_query:  # 保证至少一个查询是?
                    op_type = '?'
                else:
                    op_type = '?' if random.random() < self.query_prob else '+'
                
                k = random.randint(1, m)
                if op_type == '?':
                    s = sum(current_a[i-1] for i in sets[k-1])
                    correct_outputs.append(s)
                    queries.append(('?', k))
                    has_query = True
                else:
                    x = random.randint(-self.max_element, self.max_element)
                    for idx in sets[k-1]:
                        current_a[idx-1] += x
                    queries.append(('+', k, x))
            
            if has_query:  # 确保存在需要输出的查询
                return {
                    'n': n,
                    'm': m,
                    'q': q,
                    'a': a,
                    'sets': sets,
                    'queries': queries,
                    'correct_outputs': correct_outputs
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['q']}",
            ' '.join(map(str, question_case['a']))
        ]
        for s in question_case['sets']:
            input_lines.append(f"{len(s)} " + ' '.join(map(str, s)))
        for q in question_case['queries']:
            if q[0] == '?':
                input_lines.append(f"? {q[1]}")
            else:
                input_lines.append(f"+ {q[1]} {q[2]}")
        
        prompt = (
            "请解决数组处理问题：\n"
            "给定初始数组和多个索引集合，处理增查操作。\n"
            "规则说明：\n"
            "1. 初始数组元素为第二行数字\n"
            "2. 每个集合描述格式：大小+索引（1-based）\n"
            "3. 查询类型：\n"
            "   ? k → 输出第k个集合元素和\n"
            "   + k x → 给第k个集合元素加x\n"
            "\n输入数据：\n" + '\n'.join(input_lines) + 
            "\n\n请将每个?查询的结果按顺序放在[answer]内，如：\n[answer]\n12\n-5\n[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

