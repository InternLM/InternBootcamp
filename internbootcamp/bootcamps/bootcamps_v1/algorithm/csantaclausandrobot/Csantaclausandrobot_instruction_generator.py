import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CsantaclausandrobotInstructionGenerator(BaseInstructionGenerator):
    """Csantaclausandrobot Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20):
        """
        初始化Csantaclausandrobot指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        directions = ['L', 'R', 'U', 'D']
        movements = ''.join(random.choices(directions, k=n))
        correct_answer = self.calculate_answer(movements)
        return {
            'n': n,
            'movements': movements,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['movements']
        return f"""你是Santa的助手，需要根据机器人的移动协议确定可能的最短点序列长度。机器人移动规则如下：

1. 机器人按点序列p₁,p₂,...,pₘ移动，每次必须走两点间的最短路径
2. 移动协议中的每个字符代表一个单位移动方向（L/R/U/D）
3. 当移动方向的相反方向已在当前允许方向集中时，必须开始新的阶段并增加点序列长度

输入：
- 第一行是移动单元数n={n}
- 第二行是移动协议：{s}

请计算最小可能的点序列长度，并将答案放在[answer]和[/answer]标记之间，如：[answer]答案[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(s):
        ans = 1
        dis = set()
        rev = {'R': 'L', 'L': 'R', 'U': 'D', 'D': 'U'}
        for c in s:
            if rev[c] in dis:
                ans += 1
                dis = {c}
            else:
                dis.add(c)
        return ans
