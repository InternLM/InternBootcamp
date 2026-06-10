import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class CamrandchemistryInstructionGenerator(BaseInstructionGenerator):
    """Camrandchemistry Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Camrandchemistry指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = params.get('n', 10)
        self.max_volume = params.get('max_volume', 100000)
    
    def case_generator(self):
        n = self.n
        max_volume = self.max_volume
        
        # 选择一个目标数，确保在生成实例时总是有解
        target = random.randint(1, max_volume)
        numbers = []
        correct_operations = 0
        
        for _ in range(n):
            current = target
            steps = random.randint(0, 10)  # 调整随机步骤的范围
            
            # 生成随机的操作序列
            for _ in range(steps):
                choice = random.choice(['mult', 'div'])
                if choice == 'mult':
                    current *= 2
                else:
                    if current % 2 == 0:
                        current = current // 2
                    else:
                        current *= 2  # 如果是奇数，只能乘以2
            
            numbers.append(current)
            
            # 计算从当前数到目标数的最小操作次数
            visited = set()
            queue = deque()
            queue.append((current, 0))
            visited.add(current)
            found = False
            
            while queue:
                num, ops = queue.popleft()
                if num == target:
                    correct_operations += ops
                    found = True
                    break
                next_num = num * 2
                if next_num <= 10**6 and next_num not in visited:
                    visited.add(next_num)
                    queue.append((next_num, ops + 1))
                if num % 2 == 0:
                    next_num = num // 2
                    if next_num not in visited:
                        visited.add(next_num)
                        queue.append((next_num, ops + 1))
            
            if not found:
                # 如果无法到达目标数，重新生成当前数
                while True:
                    current = target
                    steps = random.randint(0, 10)
                    for _ in range(steps):
                        choice = random.choice(['mult', 'div'])
                        if choice == 'mult':
                            current *= 2
                        else:
                            if current % 2 == 0:
                                current = current // 2
                            else:
                                current *= 2
                    # 计算最小操作次数
                    visited = set()
                    queue = deque()
                    queue.append((current, 0))
                    visited.add(current)
                    found_inner = False
                    while queue:
                        num_inner, ops_inner = queue.popleft()
                        if num_inner == target:
                            correct_operations += ops_inner
                            found_inner = True
                            break
                        next_num_inner = num_inner * 2
                        if next_num_inner <= 10**6 and next_num_inner not in visited:
                            visited.add(next_num_inner)
                            queue.append((next_num_inner, ops_inner + 1))
                        if num_inner % 2 == 0:
                            next_num_inner = num_inner // 2
                            if next_num_inner not in visited:
                                visited.add(next_num_inner)
                                queue.append((next_num_inner, ops_inner + 1))
                    if found_inner:
                        numbers.append(current)
                        break
        
        identity = {'numbers': numbers, 'correct_operations': correct_operations}
        return identity
    
    @staticmethod
    def prompt_func(question_case):
        numbers = question_case['numbers']
        n = len(numbers)
        prompt = f"Camrandchemistry有{n}种不同的化学品，初始体积分别为：{numbers}。他需要通过乘以2或除以2（整数除法）操作，使所有化学品体积相等。请计算最小的操作次数，并将答案放在[answer]标签中，例如：[answer]5[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

