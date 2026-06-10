import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import bisect
from collections import defaultdict




class ErooksandrectanglesInstructionGenerator(BaseInstructionGenerator):
    """Erooksandrectangles Bootcamp指令生成器"""
    
    def __init__(self, n_max=50, m_max=50, k_max=20, q_max=10):
        """
        初始化Erooksandrectangles指令生成器
        
        Args:
            n_max: 参数描述
            m_max: 参数描述
            k_max: 参数描述
            q_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_max = n_max
        self.m_max = m_max
        self.k_max = k_max
        self.q_max = q_max
    
    def case_generator(self):
        n = random.randint(1, self.n_max)
        m = random.randint(1, self.m_max)
        k = random.randint(1, min(self.k_max, n * m))
        
        positions = set()
        while len(positions) < k:
            x = random.randint(1, n)
            y = random.randint(1, m)
            positions.add((x, y))
        positions = list(positions)
        
        q = random.randint(1, self.q_max)
        queries = []
        for _ in range(q):
            x1 = random.randint(1, n)
            x2 = random.randint(x1, n)
            y1 = random.randint(1, m)
            y2 = random.randint(y1, m)
            queries.append({
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            })
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'q': q,
            'rooks': positions,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        n, m, k, q = case['n'], case['m'], case['k'], case['q']
        input_lines = [f"{n} {m} {k} {q}"]
        input_lines.extend(f"{x} {y}" for x, y in case['rooks'])
        input_lines.extend(f"{q['x1']} {q['y1']} {q['x2']} {q['y2']}" for q in case['queries'])
        
        prompt = (
            "Determine if all cells in each strategic area are protected by rooks within the same area.\n"
            "Rules:\n"
            "1. A rook protects all cells in its row and column within the area, with no blocking.\n"
            "2. An area is protected if all empty cells are covered by at least one rook in the area.\n"
            "\n"
            "Input:\n" + '\n'.join(input_lines) +
            "\n\nOutput q lines of 'YES' or 'NO' wrapped in [answer]...[/answer] tags."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

