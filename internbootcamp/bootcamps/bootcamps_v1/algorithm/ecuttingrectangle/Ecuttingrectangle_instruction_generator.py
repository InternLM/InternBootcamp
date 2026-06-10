import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
from collections import defaultdict
from math import gcd




class EcuttingrectangleInstructionGenerator(BaseInstructionGenerator):
    """Ecuttingrectangle Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ecuttingrectangle指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        pass
    
    def case_generator(self):
        possible_d = [6, 12, 9, 4, 7, 8, 10]
        d = random.choice(possible_d)
        n = random.randint(1, 3)
        
        # 修正m_list生成逻辑，保证n个元素
        m_list = []
        current_gcd = 0
        for _ in range(n):
            if current_gcd == 0:
                m = random.randint(1, 5)
                current_gcd = m
            else:
                # 强制生成与current_gcd互质的m
                possible_m = [x for x in range(1, 6) if math.gcd(current_gcd, x) == 1]
                if not possible_m:  # 若无候选值，使用1（必互质）
                    m = 1
                else:
                    m = random.choice(possible_m)
                current_gcd = math.gcd(current_gcd, m)  # 更新gcd
            m_list.append(m)
        
        # 生成w_values和h_values确保长度n
        use_same_w = random.choice([True, False])
        w_values = []
        if use_same_w:
            w = random.randint(1, 1000)
            w_values = [w] * n
        else:
            used_w = set()
            while len(w_values) < n:
                w = random.randint(1, 1000)
                if w not in used_w:
                    used_w.add(w)
                    w_values.append(w)
        
        h_values = []
        used_h = set()
        while len(h_values) < n:
            h = random.randint(1, 1000)
            if h not in used_h:
                used_h.add(h)
                h_values.append(h)
        
        # 构造矩形列表
        rectangles = [{
            'w': w_values[i],
            'h': h_values[i],
            'c': d * m_list[i]
        } for i in range(n)]
        
        case = {'n': n, 'rectangles': rectangles}
        
        # 生成无效案例时不破坏列表结构
        if random.random() < 0.5 and n > 0:
            idx = random.randint(0, n-1)
            case['rectangles'][idx]['c'] += 1
        
        return case
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])]
        for rect in question_case['rectangles']:
            input_lines.append(f"{rect['w']} {rect['h']} {rect['c']}")
        problem_input = "\n".join(input_lines)
        prompt = f"""你是一个数学问题解决专家，请解决以下问题：

问题描述：
给定一个初始矩形被切割后的所有小矩形信息，计算可能的原始矩形尺寸对(A, B)的数量。注意(A, B)和(B, A)视为不同的对（当A≠B时）。

输入格式：
第一行是一个整数n，表示小矩形的不同种类数。接下来的n行每行包含三个整数w_i, h_i, c_i，分别表示第i种小矩形的宽、高和数量。

输出格式：
输出一个整数，表示符合条件的(A, B)对的数量。

示例：
输入：
1
1 1 9
输出：
3

你的任务：
输入：
{problem_input}
请将答案放在[answer]和[/answer]标签之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

