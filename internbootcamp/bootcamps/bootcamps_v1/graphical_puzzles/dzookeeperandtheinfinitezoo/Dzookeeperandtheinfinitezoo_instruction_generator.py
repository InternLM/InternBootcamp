import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DzookeeperandtheinfinitezooInstructionGenerator(BaseInstructionGenerator):
    """Dzookeeperandtheinfinitezoo Bootcamp指令生成器"""
    
    def __init__(self, u_min=1, u_max=(1 << 30)-1, v_min=1, v_max=(1 << 30)-1):
        """
        初始化Dzookeeperandtheinfinitezoo指令生成器
        
        Args:
            u_min: 参数描述
            u_max: 参数描述
            v_min: 参数描述
            v_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.u_min = u_min
        self.u_max = u_max
        self.v_min = v_min
        self.v_max = v_max
    
    def case_generator(self):
        # 生成YES案例（可达）的概率调整为40%
        if random.random() < 0.4:
            for _ in range(100):  # 总尝试次数限制
                u = random.randint(self.u_min, self.u_max)
                mask_max = min(u, self.v_max - u)
                if mask_max < 0:
                    continue
                for _ in range(100):  # 单u尝试次数
                    mask = random.randint(0, mask_max)
                    v_prime = u & mask
                    v = u + v_prime
                    if self.v_min <= v <= self.v_max:
                        return {'u': u, 'v': v}
            # 若无法生成有效YES案例，退回生成NO案例
            return self._generate_no_case()
        else:
            return self._generate_no_case()
    
    @staticmethod
    def prompt_func(question_case):
        u = question_case['u']
        v = question_case['v']
        return f"""Determine if path exists from {u} to {v} in Infinite Zoo.
Rules:
1. Edge u→(u+v') exists iff u & v' = v'
2. Path follows edge directions

Answer format: [answer]YES[/answer] or [answer]NO[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_no_case(self):
        """ 专门生成NO案例的方法 """
        # 首先生成u>v的情况（40%概率）
        if random.random() < 0.4:
            v = random.randint(self.v_min, self.u_max-1)
            u = random.randint(v+1, self.u_max)
            return {'u': u, 'v': v}
        # 生成u<=v但不可达的情况（最多尝试200次）
        for _ in range(200):
            u = random.randint(self.u_min, self.u_max)
            v = random.randint(u, self.v_max)
            if not self.is_reachable(u, v):
                return {'u': u, 'v': v}
        # 最终保障机制：生成u>v的简单案例
        v = random.randint(self.v_min, self.u_max-1)
        u = random.randint(v+1, self.u_max)
        return {'u': u, 'v': v}

    @staticmethod
    def is_reachable(u, v):
        if u > v:
            return False
        x = y = 0
        for _ in range(31):
            x += u & 1
            y += v & 1
            if y > x:
                return False
            u >>= 1
            v >>= 1
        return True
