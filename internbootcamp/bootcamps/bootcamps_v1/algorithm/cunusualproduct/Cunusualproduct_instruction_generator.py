import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CunusualproductInstructionGenerator(BaseInstructionGenerator):
    """Cunusualproduct Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cunusualproduct指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.pop('n', 3)
        self.q = params.pop('q', 5)
        self.random_seed = params.pop('random_seed', None)
        super().__init__(**params)
    
    def case_generator(self):
        if self.random_seed is not None:
            random.seed(self.random_seed)
        
        n = self.n
        q = self.q
        
        # 生成全随机矩阵
        matrix = []
        initial_S = 0
        for i in range(n):
            row = [random.choice([0, 1]) for _ in range(n)]
            matrix.append(row)
            initial_S ^= row[i]  # 对角线元素异或
        
        queries = []
        type3_count = 0
        for _ in range(q):
            if type3_count == 0 and len(queries) == q - 1:
                query_type = 3
            else:
                query_type = random.choices([1, 2, 3], weights=[2, 2, 1], k=1)[0]
            
            if query_type == 3:
                queries.append({'type': 3})
                type3_count += 1
            else:
                i = random.randint(1, n)
                queries.append({'type': query_type, 'i': i})
        
        return {
            'n': n,
            'matrix': matrix,
            'queries': queries,
            'flip_count': 0  # 初始翻转次数
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = (
            "Little Chris needs to process matrix operations in GF(2). The unusual square is the XOR sum of diagonal elements.\n\n"
            f"Matrix Size: {question_case['n']}x{question_case['n']}\n"
            "Matrix Values:\n"
        )
        for row in question_case['matrix']:
            prompt += ' '.join(map(str, row)) + '\n'
        prompt += f"\nQueries ({len(question_case['queries'])}):\n"
        for q in question_case['queries']:
            if q['type'] == 3:
                prompt += "3\n"
            else:
                prompt += f"{q['type']} {q['i']}\n"
        prompt += (
            "\nOutput the binary results of all type 3 queries as a continuous string.\n"
            "Enclose your answer with [answer] and [/answer] tags.\n"
            "Example: [answer]0110[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

