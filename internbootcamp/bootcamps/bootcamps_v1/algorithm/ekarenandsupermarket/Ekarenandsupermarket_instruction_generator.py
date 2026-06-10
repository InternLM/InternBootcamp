import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EkarenandsupermarketInstructionGenerator(BaseInstructionGenerator):
    """Ekarenandsupermarket Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, c_range=(5, 20), d_ratio=0.5, **kwargs):
        """
        初始化Ekarenandsupermarket指令生成器
        
        Args:
            max_n: 参数描述
            c_range: 参数描述
            d_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.c_range = c_range
        self.d_ratio = d_ratio
        super().__init__(**kwargs)
    
    def case_generator(self):
        """Generate a valid test case with tree-structured coupon dependencies"""
        n = random.randint(1, self.max_n)
        items = []
        dependency_tree = {1: []}
        
        for i in range(1, n+1):
            ci = random.randint(*self.c_range)
            di = random.randint(max(1, int(ci * self.d_ratio)), ci-1)
            
            if i == 1:
                items.append({'c': ci, 'd': di})
            else:
                xi = random.choice(list(dependency_tree.keys()))
                items.append({'c': ci, 'd': di, 'x': xi})
                dependency_tree[i] = []
                dependency_tree[xi].append(i)
        
        # Calculate reasonable budget range
        min_cost = sum(item['c'] - item['d'] for item in items)
        max_cost = sum(item['c'] for item in items)
        b = random.randint(
            int(min_cost * 0.5),
            max_cost + random.randint(0, sum(item['d'] for item in items))
        )
        
        return {
            'n': n,
            'b': b,
            'items': items,
            'dependency_tree': dependency_tree
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [f"{question_case['n']} {question_case['b']}"]
        for i, item in enumerate(question_case['items'], 1):
            if i == 1:
                input_lines.append(f"{item['c']} {item['d']}")
            else:
                input_lines.append(f"{item['c']} {item['d']} {item['x']}")
        
        return f"""Karen wants to maximize purchased goods with coupons under dependency constraints. Rules:
1. Each product has a coupon that reduces price by di (must buy the product to use)
2. For i≥2, using coupon i requires using coupon xi (which may have its own dependencies)
3. Budget cannot exceed b dollars
4. Each product can be bought at most once

Input format:
n b
c1 d1 (first product, no dependency)
c2 d2 x2 (subsequent products show dependency)
...
cn dn xn

Current input:
{chr(10).join(input_lines)}

Calculate the maximum number of items Karen can buy within budget. Put only the integer answer within [answer]...[/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

