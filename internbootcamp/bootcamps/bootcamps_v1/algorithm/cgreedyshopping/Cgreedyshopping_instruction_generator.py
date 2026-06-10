import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import accumulate




class CgreedyshoppingInstructionGenerator(BaseInstructionGenerator):
    """Cgreedyshopping Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cgreedyshopping指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 10)
        self.q = params.get('q', 5)
        self.n = max(1, self.n)  # 确保最小为1
        self.q = max(1, self.q)  # 确保至少一个查询
    
    def case_generator(self):
        # 生成非递增数组（优化版）
        a = [random.randint(1, 10**9)]
        for _ in range(1, self.n):
            a.append(random.randint(1, a[-1]))
        
        # 生成查询列表并确保类型2存在
        queries = []
        type2_indices = []
        for i in range(self.q):
            t = random.choices([1, 2], weights=[0.4, 0.6])[0]  # 增加类型2概率
            x = random.randint(1, self.n)
            y = random.randint(1, 10**9)
            queries.append([t, x, y])  # 统一使用列表存储
            if t == 2:
                type2_indices.append(i)

        # 确保至少一个类型2查询
        if not type2_indices:
            queries[-1] = [2, random.randint(1, self.n), random.randint(1, 10**9)]
            type2_indices = [self.q-1]

        # 预处理答案（优化模拟）
        current_a = a.copy()
        answers = []
        for op in queries:
            t, x, y = op
            if t == 1:
                # 使用二分查找确定有效更新范围
                left = 0
                right = x-1  # 转换为0-based索引
                update_pos = next((i for i in range(x) if current_a[i] < y), None)
                if update_pos is not None:
                    current_a[update_pos:x] = [max(y, val) for val in current_a[update_pos:x]]
            else:
                # 使用累积和优化计算
                prefix = list(accumulate(current_a[x-1:]))
                money = y
                count = 0
                for s in prefix:
                    if s > money:
                        break
                    count += 1
                    money -= s - (prefix[count-2] if count>1 else 0)
                answers.append(count)

        return {
            'n': self.n,
            'q': self.q,
            'initial_array': a,
            'queries': queries,  # 统一使用列表存储
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['q']}",
            ' '.join(map(str, question_case['initial_array']))
        ]
        for op in question_case['queries']:
            input_lines.append(f"{op[0]} {op[1]} {op[2]}")

        return f"""你正在处理餐馆消费查询系统，需要处理两种操作类型：

**规则详解**
1. 类型1 (1 x y)：将前x个餐馆的餐费更新为原值和y的较大值
2. 类型2 (2 x y)：顾客从第x个餐馆开始向后消费，直到余额不足

**输入格式**
{" ".join(input_lines[:2])}
{chr(10).join(input_lines[2:])}

**答案格式要求**
请将所有类型2查询的答案按顺序排列在[answer]标签内，例如：
[answer]
3
5
2
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

