import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcircularrmqInstructionGenerator(BaseInstructionGenerator):
    """Ccircularrmq Bootcamp指令生成器"""
    
    def __init__(self, n_range=(4, 10), m_range=(3, 8), **params):
        """
        初始化Ccircularrmq指令生成器
        
        Args:
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = n_range
        self.m_range = m_range
        super().__init__(**params)
    
    def case_generator(self):
        n = random.randint(*self.n_range)
        array = [random.randint(-10, 10) for _ in range(n)]
        m = random.randint(*self.m_range)
        operations = []
        expected_outputs = []
        current_array = array.copy()
        
        for _ in range(m):
            if random.random() < 0.5:
                # Generate inc operation
                lf = random.randint(0, n-1)
                rg = random.randint(0, n-1)
                v = random.randint(-5, 5)
                operations.append({'type': 'inc', 'lf': lf, 'rg': rg, 'v': v})
                
                # Apply inc to current_array
                if lf <= rg:
                    for i in range(lf, rg+1):
                        current_array[i] += v
                else:
                    for i in range(lf, n):
                        current_array[i] += v
                    for i in range(0, rg+1):
                        current_array[i] += v
            else:
                # Generate rmq operation
                lf = random.randint(0, n-1)
                rg = random.randint(0, n-1)
                operations.append({'type': 'rmq', 'lf': lf, 'rg': rg})
                
                # Calculate min value
                min_val = float('inf')
                if lf <= rg:
                    for i in range(lf, rg+1):
                        if current_array[i] < min_val:
                            min_val = current_array[i]
                else:
                    for i in range(lf, n):
                        if current_array[i] < min_val:
                            min_val = current_array[i]
                    for i in range(0, rg+1):
                        if current_array[i] < min_val:
                            min_val = current_array[i]
                expected_outputs.append(min_val)
        
        return {
            'n': n,
            'array': array,
            'operations': operations,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        array_str = ' '.join(map(str, question_case['array']))
        m = len(question_case['operations'])
        input_lines = [str(n), array_str, str(m)]
        for op in question_case['operations']:
            if op['type'] == 'inc':
                line = f"{op['lf']} {op['rg']} {op['v']}"
            else:
                line = f"{op['lf']} {op['rg']}"
            input_lines.append(line)
        input_data = '\n'.join(input_lines)
        
        prompt = f"""你是一个编程竞赛的参赛者，需要解决以下问题：

给定一个长度为{n}的循环数组，处理一系列操作并输出结果。数组初始值为：{array_str}。

操作类型：
1. inc lf rg v：将循环区间[lf, rg]内的每个元素增加v。当lf <= rg时，区间是连续的；否则包含数组末尾到开头。
2. rmq lf rg：查询循环区间[lf, rg]内的最小值。

输入格式：
{input_data}

请处理所有操作，并按顺序输出每个rmq操作的结果。将结果按顺序放在[answer]和[/answer]标签之间，每个结果占一行。

例如，若结果应为1、0、0，则正确格式为：
[answer]
1
0
0
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

