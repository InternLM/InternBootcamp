import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CchocolatebunnyInstructionGenerator(BaseInstructionGenerator):
    """Cchocolatebunny Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cchocolatebunny指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        动态参数配置，支持自定义排列长度
        """
        self.n = params.get('n', 3)
        if not 1 <= self.n <= 10**4:
            raise ValueError("n must be between 1 and 10^4")
    
    def case_generator(self):
        """通用的排列生成方法"""
        permutation = list(range(1, self.n + 1))
        if self.n > 1:
            random.shuffle(permutation)
        return {'n': self.n, 'permutation': permutation}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """精确的提示生成逻辑"""
        n = question_case['n']
        example = ' '.join(map(str, question_case['permutation']))
        return f"""编程竞赛交互题规则：
        
我们需要找出长度为{n}的排列p。你最多可以进行{2*n}次询问，每次询问格式为"? x y"（x≠y），系统返回p_x mod p_y的值。

你的任务是：
1. 分析模运算结果间的逻辑关系
2. 推断出完整排列
3. 按格式输出答案：! 后跟排列的数字，用空格分隔

请直接将最终答案放入[answer]标签内，例如：
[answer]
! {example}
[/answer]

现在请解决n={n}的案例：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

