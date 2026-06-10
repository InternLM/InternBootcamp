import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CjonsnowandhisfavouritenumberInstructionGenerator(BaseInstructionGenerator):
    """Cjonsnowandhisfavouritenumber Bootcamp指令生成器"""
    
    def __init__(self, max_n=100000, max_k=100000, max_x=1000, max_strength=1000):
        """
        初始化Cjonsnowandhisfavouritenumber指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
            max_x: 参数描述
            max_strength: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k
        self.max_x = max_x
        self.max_strength = max_strength
    
    def case_generator(self):
        # 生成边界用例的概率提升到30%
        if random.random() < 0.3:
            n = random.choice([1, 100000, 1000])
            k = random.choice([0, 100000, 50000])
            x = random.choice([0, 1000])
            strengths = ([random.choice([0, 1000])] * n) if n > 1 else [random.randint(0, 1000)]
        else:
            n = random.randint(1, self.max_n)
            k = random.randint(0, self.max_k)
            x = random.randint(0, self.max_x)
            strengths = [random.randint(0, self.max_strength) for _ in range(n)]
        
        return {
            'n': n,
            'k': k,
            'x': x,
            'strengths': strengths
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        params = question_case
        return f"""Jon Snow需要计算{r'大写的' if params['x'] > 500 else ''}游骑兵部队的最终战力。经过{params['k']}次特殊操作后：
        
**操作规则**
1. 每次操作前按战力升序排列
2. 对奇数位(1st,3rd,5th...)的战士进行XOR运算，使用的值为{params['x']}

**初始数据**
- 战士数量: {params['n']}
- 操作次数: {params['k']}
- XOR值: {params['x']}
- 初始战力: {' '.join(map(str, params['strengths']))}

请输出最终的最大和最小战力，格式示例：
[answer]1024 0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

