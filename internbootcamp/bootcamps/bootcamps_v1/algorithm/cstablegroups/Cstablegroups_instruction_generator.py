import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CstablegroupsInstructionGenerator(BaseInstructionGenerator):
    """Cstablegroups Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cstablegroups指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'n_min': params.get('n_min', 1),   # 允许生成n=0/1的边界情况
            'n_max': params.get('n_max', 10),
            'x_min': params.get('x_min', 1),
            'x_max': params.get('x_max', 10),
            'k_max': params.get('k_max', 10**18),
            'a_max': params.get('a_max', 10**18),
        }
    
    def case_generator(self):
        params = self.params
        n = random.randint(params['n_min'], params['n_max'])
        x = random.randint(params['x_min'], params['x_max'])
        
        # 生成混合包含稳定间隔和非稳定间隔的测试用例
        a_sorted = []
        if n > 0:
            a_sorted = [random.randint(1, 100)]
            for _ in range(n-1):
                # 50%概率生成稳定间隔（包括重复值）
                if random.random() < 0.5:
                    delta = random.randint(0, x)
                else:
                    delta = x + random.randint(1, 10)
                a_sorted.append(a_sorted[-1] + delta)
            a_sorted.sort()

        # 计算所有需要填补的间隙
        gaps = []
        for i in range(1, len(a_sorted)):
            d = a_sorted[i] - a_sorted[i-1]
            if d > x:
                req = (d-1) // x  # 等效于 d//x 的向上取整减一
                gaps.append(req)
        gaps.sort()

        # 生成合理的k值（允许k为0或覆盖部分间隙）
        k_val = 0
        if len(gaps) > 0:
            cover = random.randint(0, len(gaps))
            required = sum(gaps[:cover])
            k_val = min(required, params['k_max'])
        else:
            # 无间隙时k仍然可以随机设置（不影响结果）
            k_val = random.randint(0, params['k_max'])

        return {
            'n': n,
            'k': k_val,
            'x': x,
            'a': a_sorted
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""You need to split students into stable groups. Two rules:
1. A group is stable if adjacent student level differences ≤ {question_case['x']}
2. You can add up to {question_case['k']} students with any levels

Students (sorted): {question_case['a']}
Output the minimal number of groups. Put answer in [answer][/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

