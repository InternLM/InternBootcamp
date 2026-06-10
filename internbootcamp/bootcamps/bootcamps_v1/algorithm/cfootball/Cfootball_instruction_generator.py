import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CfootballInstructionGenerator(BaseInstructionGenerator):
    """Cfootball Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, max_k=1000):
        """
        初始化Cfootball指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数设置生成n和k的最大值，确保案例多样性。
        """
        self.max_n = max_n
        self.max_k = max_k
    
    def case_generator(self):
        """
        生成随机案例，覆盖有效（k合法）和无效（k过大）两种情况。
        """
        n = random.randint(1, self.max_n)
        if random.random() < 0.5:  # 50%概率生成有效案例
            if n == 1:
                k = 0  # n=1时k只能为0
            else:
                max_valid_k = (n - 1) // 2
                k = random.randint(0, max_valid_k)
        else:  # 50%概率生成无效案例
            if n == 1:
                k = random.randint(1, self.max_k)  # 若n=1，k>0则无解
            else:
                min_invalid_k = (n - 1) // 2 + 1
                k = random.randint(min_invalid_k, min(self.max_k, min_invalid_k + 100))
        return {"n": n, "k": k}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case["n"]
        k = question_case["k"]
        return f"""You are to solve a football tournament problem where each team must beat exactly k others. The teams are numbered 1 to {n}, and each pair can play at most once.

Input:
n = {n}, k = {k}

Output:
- If possible, the number of matches followed by each match (winner and loser).
- If impossible, output -1.

Format your answer within [answer] and [/answer] tags. Example for n=3, k=1:
[answer]
3
1 2
2 3
3 1
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

