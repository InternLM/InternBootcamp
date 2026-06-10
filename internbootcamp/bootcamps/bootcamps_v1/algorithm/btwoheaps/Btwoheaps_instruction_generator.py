import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import re
import random




class BtwoheapsInstructionGenerator(BaseInstructionGenerator):
    """Btwoheaps Bootcamp指令生成器"""
    
    def __init__(self, n_range=(1, 5), num_range=(10, 99)):
        """
        初始化Btwoheaps指令生成器
        
        Args:
            n_range: 参数描述
            num_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = n_range
        self.num_range = num_range
    
    def case_generator(self):
        # 生成至少包含重复数字的合法案例
        n = random.randint(*self.n_range)
        a = []
        # 确保至少有一个重复数
        for _ in range(2*n//2):
            num = random.randint(*self.num_range)
            a.extend([num]*2)
        # 补充剩余数字（如果存在奇数个）
        while len(a) < 2*n:
            a.append(random.randint(*self.num_range))
        random.shuffle(a)
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        problem = f"""Valera有2·n个立方体，每个立方体上的数字是10到99的整数。现在需要将这些立方体分成两个堆，每个堆各n个，使得可能生成的不同的四位数数目最大。你的任务是找到这样的分堆方法，并输出最大数目和对应的堆分配方案。

输入：
第一行是n的值，即{n}。
第二行是{2*n}个用空格分隔的数字：{a_str}。

输出：
第一行输出一个整数，表示最大可能的四位数数目。
第二行输出{2*n}个用空格分隔的1或2，表示每个立方体属于哪个堆。1表示第一个堆，2表示第二个堆。必须保证每个堆恰好有n个立方体。

请将答案按照严格格式放在[answer]标签内，例如：
[answer]
4
1 2 2 1
[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

