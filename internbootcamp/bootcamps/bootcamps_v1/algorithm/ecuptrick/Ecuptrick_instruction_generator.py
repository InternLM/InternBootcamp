import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EcuptrickInstructionGenerator(BaseInstructionGenerator):
    """Ecuptrick Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ecuptrick指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(2, 5))
        self.m = params.get('m', random.randint(1, 3))
        self.gen_valid_operations = params.get('gen_valid', True)  # 控制生成合法操作
    
    def case_generator(self):
        """逆向生成合法的操作序列"""
        n, m = self.n, self.m
        
        # 生成目标排列
        final = list(range(1, n+1))
        random.shuffle(final)
        
        # 逆向构造操作序列
        operations = []
        pos_dict = {x: i+1 for i, x in enumerate(final)}  # 当前每个杯子位置
        
        for _ in range(m):
            # 选择要移动的杯子(不能重复)
            candidates = list(pos_dict.keys())
            if not candidates: break
            xi = random.choice(candidates)
            
            # 当前实际位置
            yi = pos_dict[xi]
            operations.append((xi, yi))
            
            # 逆向操作：将xi移到位置yi (逆向即需要先将它放在最前面)
            del pos_dict[xi]
            pos_dict = {k: v+1 for k, v in pos_dict.items()}  # 其他杯子后移
            pos_dict[xi] = 1  # 新插入到最前面
            
        operations.reverse()  # 反向存储操作顺序
        
        # 计算初始排列
        initial = sorted(pos_dict.items(), key=lambda x: x[1])
        initial = [x[0] for x in initial]
        
        return {
            'n': n,
            'm': m,
            'operations': operations,
            'correct_answer': initial
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        ops = '\n'.join(f"{xi} {yi}" for xi, yi in question_case['operations'])
        return f"""Given {n} cups and {m} operations, find the lex-min initial permutation. Operations are given in chronological order. Each operation moves cup xi from position yi to front. Output -1 if impossible. Put your answer between [answer] and [/answer].

Input:
{n} {m}
{ops}

Example:
[answer]
1 2 3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

