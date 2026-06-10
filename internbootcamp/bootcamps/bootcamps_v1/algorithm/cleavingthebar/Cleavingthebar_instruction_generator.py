import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
import re




class CleavingthebarInstructionGenerator(BaseInstructionGenerator):
    """Cleavingthebar Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=1000, max_vector_length=10**6):
        """
        初始化Cleavingthebar指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_vector_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_vector_length = max_vector_length
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        vectors = []
        max_len = self.max_vector_length
        for _ in range(n):
            # 随机选择轴对齐或任意方向
            if random.random() < 0.3:  # 30%概率生成轴对齐向量
                axis = random.choice(['x', 'y'])
                sign = random.choice([1, -1])
                r = random.randint(0, max_len)
                vec = (sign*r, 0) if axis == 'x' else (0, sign*r)
            else:  # 70%概率生成任意方向向量
                while True:
                    x = random.randint(-max_len, max_len)
                    y = random.randint(-max_len, max_len)
                    if x**2 + y**2 <= max_len**2:
                        break
                vec = (x, y)
            vectors.append(vec)
        return {'n': n, 'vectors': vectors}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        vectors = question_case['vectors']
        vectors_str = '\n'.join(f"{x} {y}" for x, y in vectors)
        return f"""Allen醉后需要从酒吧原点出发完成{n}次移动，每次沿±向量方向移动。请选择移动方向使得最终位置距离原点不超过1.5×10^6。

输入格式：
第一行为n
接下来n行每行两个整数x_i y_i

输入：
{n}
{vectors_str}

输出要求：
一行n个1/-1，1表示沿原向量方向，-1表示反向
答案请包裹在[answer]标签内，例如：[answer]1 -1 1 ...[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

