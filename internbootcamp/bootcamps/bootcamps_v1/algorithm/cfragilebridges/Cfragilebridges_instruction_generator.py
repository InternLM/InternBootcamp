import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CfragilebridgesInstructionGenerator(BaseInstructionGenerator):
    """Cfragilebridges Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, min_n=2, ai_max=10**9):
        """
        初始化Cfragilebridges指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
            ai_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_n = min_n
        self.ai_max = ai_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        ai = [random.randint(1, self.ai_max) for _ in range(n-1)]
        return {
            'n': n,
            'ai': ai,
            'correct_answer': self.compute_max_points(n, ai)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        ai = question_case['ai']
        input_str = f"{n}\n{' '.join(map(str, ai))}"
        prompt = f"""You are playing a video game bonus level with platforms connected by bridges. Each bridge has a durability indicating how many times it can be crossed.

Task:
Find the maximum transitions possible before bridges collapse.

Input Format:
{n}
{' '.join(map(str, ai))}

Answer format: [answer]integer[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_points(n, a):
        if n < 2:
            return 0
        dpbackR = [0] * n
        for x in range(n-2, -1, -1):
            if a[x] <= 1:
                dpbackR[x] = 0
            else:
                val = a[x] if a[x] % 2 == 0 else a[x] - 1
                dpbackR[x] = val + dpbackR[x+1]

        dpR = [0] * n
        for x in range(n-2, -1, -1):
            if a[x] % 2 == 0:
                option1 = (a[x] - 1) + dpR[x+1]
            else:
                option1 = a[x] + dpR[x+1]
            option2 = dpbackR[x]
            dpR[x] = max(option1, option2)

        dpbackL = [0] * n
        for x in range(1, n):
            if a[x-1] <= 1:
                dpbackL[x] = 0
            else:
                val = a[x-1] if a[x-1] % 2 == 0 else a[x-1] - 1
                dpbackL[x] = val + dpbackL[x-1]

        dpL = [0] * n
        for x in range(1, n):
            if a[x-1] % 2 == 0:
                option1 = (a[x-1] - 1) + dpL[x-1]
            else:
                option1 = a[x-1] + dpL[x-1]
            option2 = dpbackL[x]
            dpL[x] = max(option1, option2)

        best = 0
        for i in range(n):
            best = max(best, dpbackL[i] + max(dpbackR[i], dpR[i]))
            best = max(best, dpbackR[i] + max(dpbackL[i], dpL[i]))
        return best
