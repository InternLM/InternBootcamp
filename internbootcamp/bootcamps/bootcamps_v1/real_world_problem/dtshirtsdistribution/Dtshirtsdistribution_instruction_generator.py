import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DtshirtsdistributionInstructionGenerator(BaseInstructionGenerator):
    """Dtshirtsdistribution Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dtshirtsdistribution指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_participants = params.get('min_participants', 1)
        self.max_participants = params.get('max_participants', 10)
        self.double_prob = params.get('double_prob', 0.3)
    
    def case_generator(self):
        """保证生成有解的实例"""
        n = random.randint(self.min_participants, self.max_participants)
        
        # 首先生成实际分配方案
        assignments = []
        for _ in range(n):
            size_idx = random.randint(0, 5)
            assignments.append(size_idx)
        
        # 计算库存
        inventory = [0]*6
        for idx in assignments:
            inventory[idx] += 1
        
        # 生成需求描述
        demands = []
        for idx in assignments:
            if random.random() < self.double_prob and idx < 5:
                # 生成相邻需求（确保至少包含实际尺寸）
                neighbor = random.choice([idx, idx+1])
                min_idx = min(idx, neighbor)
                max_idx = max(idx, neighbor)
                demands.append(f"{self.SIZES[min_idx]},{self.SIZES[max_idx]}")
            else:
                demands.append(self.SIZES[idx])
        
        return {
            'available': inventory,
            'n': n,
            'demands': demands
        }
    
    @staticmethod
    def prompt_func(question_case):
        sizes = ' '.join(map(str, question_case['available']))
        demands = '\n'.join(question_case['demands'])
        return f"""编程竞赛T恤分配问题：
可用尺寸库存（S M L XL XXL XXXL）：{sizes}
参与者数量：{question_case['n']}
需求列表：
{demands}

请判断是否可以满足所有需求，并将答案包裹在[answer]标签中。例如：
[answer]
YES
XL
M
XXL
[/answer]
或：
[answer]
NO
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

