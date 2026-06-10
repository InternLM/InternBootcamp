import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CarraydestructionInstructionGenerator(BaseInstructionGenerator):
    """Carraydestruction Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=3, elem_min=1, elem_max=10, solvable_prob=0.5):
        """
        初始化Carraydestruction指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            elem_min: 参数描述
            elem_max: 参数描述
            solvable_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.elem_min = elem_min
        self.elem_max = elem_max
        self.solvable_prob = solvable_prob
    
    def case_generator(self):
        generate_solvable = random.random() < self.solvable_prob
        if generate_solvable:
            # 构造可解案例
            while True:
                n = random.randint(self.n_min, self.n_max)
                size = 2 * n
                a = sorted([random.randint(self.elem_min, self.elem_max) for _ in range(size)], reverse=True)
                # 确保可解
                if Carraydestructionbootcamp.check_solvable(n, a):
                    random.shuffle(a)  # 打乱数组顺序
                    return {'n': n, 'a': a}
        else:
            # 生成不可解案例
            while True:
                n = random.randint(self.n_min, self.n_max)
                a = [random.randint(self.elem_min, self.elem_max) for _ in range(2 * n)]
                if not Carraydestructionbootcamp.check_solvable(n, a.copy()):
                    return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        case_str = ' '.join(map(str, a))
        prompt = (
            "You are given an array elimination puzzle. Your task is to determine if it's possible to remove all elements of the array by following specific rules.\n\n"
            "Rules:\n"
            "1. Choose a positive integer x initially.\n"
            "2. Perform n operations. In each operation:\n"
            "   - Select two elements whose sum equals the current x.\n"
            "   - Remove them and update x to the maximum of the two selected elements.\n\n"
            f"Input:\nThe array has {2*n} elements: {case_str}\n\n"
            "Output:\n"
            "If possible, output YES followed by the initial x and the pairs removed in each operation.\n"
            "If not possible, output NO.\n\n"
            "Format your answer as:\n"
            "[answer]\n"
            "YES\n<initial_x>\n<element1> <element2>\n...\n[/answer]\n"
            "or\n"
            "[answer]\nNO\n[/answer]\n"
            "Include ONLY the [answer] block in your response."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def check_solvable(n, a_original):
        a = sorted(a_original.copy(), reverse=True)
        m = 2 * n
        d = {}
        prev = None
        for i in range(m):
            if i == 0 or a[i] != prev:
                d[a[i]] = i
                prev = a[i]

        for i in range(1, m):
            if i > 1 and a[i] == a[i-1]:
                continue
            p = d.copy()
            s = a[0] + a[i]
            b = [0] * m
            k = 0
            valid = True
            for _ in range(n):
                while k < m and b[k]:
                    k += 1
                if k >= m:
                    valid = False
                    break
                x = a[k]
                if x not in p:
                    valid = False
                    break
                p[x] += 1
                y = s - x
                if y not in p or x < y:
                    valid = False
                    break
                l = p[y]
                if l >= m or a[l] != y:
                    valid = False
                    break
                b[k] = 1
                b[l] = 1
                s = x
                k += 1
            if valid:
                return True
        return False
