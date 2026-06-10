import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DpowerfulkseniaInstructionGenerator(BaseInstructionGenerator):
    """Dpowerfulksenia Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10, possible=None):
        """
        初始化Dpowerfulksenia指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            possible: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(3, min_n)
        self.max_n = max(self.min_n, max_n)
        self.possible = possible
    
    def case_generator(self):
        if self.possible is not None:
            should_generate_possible = self.possible
        else:
            should_generate_possible = random.choice([True, False])
        
        if should_generate_possible:
            # 确定可行的生成类型
            generate_odd = False
            possible_odd = [x for x in range(self.min_n, self.max_n+1) if x%2 == 1]
            possible_even = [x for x in range(max(4, self.min_n), self.max_n+1) if x%2 == 0]
            
            # 动态选择生成类型
            if possible_odd and possible_even:
                generate_odd = random.choice([True, False])
            elif possible_odd:
                generate_odd = True
            elif possible_even:
                generate_odd = False
            else:
                raise ValueError("No valid n in given range")
            
            if generate_odd:
                n = random.choice(possible_odd)
                elements = [random.randint(1, 10) for _ in range(n)]
                return {'n': n, 'a': elements}
            else:
                n = random.choice(possible_even)
                elements = [random.randint(1, 10) for _ in range(n-1)]
                total_xor = 0
                for num in elements:
                    total_xor ^= num
                elements.append(total_xor)
                return {'n': n, 'a': elements}
        else:
            # 生成不可能的偶数案例
            possible_even = [x for x in range(max(4, self.min_n), self.max_n+1) if x%2 == 0]
            if not possible_even:
                raise ValueError("No even n in given range for impossible case")
            n = random.choice(possible_even)
            elements = [random.randint(1, 10) for _ in range(n-1)]
            total_xor = 0
            for num in elements:
                total_xor ^= num
            elements.append(total_xor ^ random.randint(1, 10))
            return {'n': n, 'a': elements}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        return (
            f"Problem: Given array of {n} integers: {', '.join(map(str, a))}\n"
            "Operation: Choose 3 distinct indices and set all to their XOR\n"
            "Task: Determine if achievable in ≤n operations\n"
            "Answer format:\n"
            "[answer]\n"
            "YES/NO\n"
            "m\n"
            "i j k\n"
            "...\n"
            "[/answer]\n"
            "Note: Indices must be 1-based"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

