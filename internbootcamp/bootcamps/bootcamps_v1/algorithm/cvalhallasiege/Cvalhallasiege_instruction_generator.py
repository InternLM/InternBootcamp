import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CvalhallasiegeInstructionGenerator(BaseInstructionGenerator):
    """Cvalhallasiege Bootcamp指令生成器"""
    
    def __init__(self, n=5, q=5, max_a=10**9, max_k=10**14):
        """
        初始化Cvalhallasiege指令生成器
        
        Args:
            n: 参数描述
            q: 参数描述
            max_a: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.q = q
        self.max_a = max_a
        self.max_k = max_k
    
    def case_generator(self):
        a = [random.randint(1, self.max_a) for _ in range(self.n)]
        sum_a = sum(a)
        
        k = []
        for _ in range(self.q):
            if random.random() < 0.2:
                ki = random.randint(sum_a//2, self.max_k)
            else:
                upper = min(sum_a*2, self.max_k)
                ki = random.randint(1, upper)
            k.append(ki)
        
        return {
            'n': self.n,
            'q': self.q,
            'a': a,
            'k': k,
            'sum_a': sum_a
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Ivar的战士排成一列面对城堡大门。每个战士能承受的箭数为a_i。战斗持续q分钟，每分钟射出k_i支箭，箭依次攻击存活的第一个战士。当所有战士倒下时，当前分钟剩余箭矢报废，战士立即复活。请计算每分钟后的存活战士数。

输入格式：
第一行：n={question_case['n']} q={question_case['q']}
第二行：{' '.join(map(str, question_case['a']))}
第三行：{' '.join(map(str, question_case['k']))}

输出{question_case['q']}行，每行一个整数表示存活数。请将答案严格按以下格式放置：

[answer]
示例答案（共{question_case['q']}行）：
3
5
4
...
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

