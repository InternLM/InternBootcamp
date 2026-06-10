import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EgreedyshoppingInstructionGenerator(BaseInstructionGenerator):
    """Egreedyshopping Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_q=5, max_value=1000, type1_ratio=0.5):
        """
        初始化Egreedyshopping指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_value: 参数描述
            type1_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_value = max_value
        self.type1_ratio = type1_ratio
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        q = random.randint(1, self.max_q)
        a_initial = sorted([random.randint(1, self.max_value) for _ in range(n)], reverse=True)
        queries = []
        has_type2 = False
        
        # Generate queries with guarantee at least one type2
        for i in range(q):
            if i == q-1 and not has_type2:
                t = 2
            else:
                t = 1 if random.random() < self.type1_ratio else 2
            
            x = random.randint(1, n)
            # Enhance y generation logic for type1
            if t == 1:
                current_max = max(a_initial[:x]) if x <= len(a_initial) else 0
                y = random.randint(
                    max(1, current_max - 5), 
                    current_max + self.max_value//2
                )
            else:
                total_max = sum(a_initial)
                y = random.randint(1, total_max * 2)
                has_type2 = True
            
            queries.append((t, x, y))

        # Simulate operations
        a = a_initial.copy()
        answers = []
        for t, x, y in queries:
            if t == 1:
                # Find last position where a[i] <= y to maintain non-increasing property
                new_val = y
                left = 0
                right = min(x, len(a)) - 1
                pos = -1
                while left <= right:
                    mid = (left + right) // 2
                    if a[mid] <= new_val:
                        pos = mid
                        right = mid - 1
                    else:
                        left = mid + 1
                
                if pos != -1:
                    fill_val = max(a[pos], new_val) if pos < len(a) else new_val
                    for i in range(pos, min(x, len(a))):
                        a[i] = max(a[i], fill_val)
            else:
                money = y
                count = 0
                for i in range(x-1, len(a)):
                    if money >= a[i]:
                        count += 1
                        money -= a[i]
                answers.append(count)
        
        return {
            'n': n,
            'q': q,
            'initial_array': a_initial,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['q']}",
            ' '.join(map(str, question_case['initial_array']))
        ]
        for t, x, y in question_case['queries']:
            input_lines.append(f"{t} {x} {y}")
        input_str = '\n'.join(input_lines)
        
        return f"""你需要解决一个算法问题：

给定一个非递增的整数数组，处理q个查询：
1. 类型1 (1 x y)：将前x个元素更新为max(a_i, y)
2. 类型2 (2 x y)：从第x个商店开始消费y元，计算能购买多少餐

输入格式：
第一行：n q
第二行：初始数组（保证非递增）
随后q行：每行包含t x y

输入数据：
{input_str}

请将每个类型2查询的答案按顺序放在[answer]标签内，如：
[answer]
结果1
结果2
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

