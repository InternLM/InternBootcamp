import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DgamewithpowersInstructionGenerator(BaseInstructionGenerator):
    """Dgamewithpowers Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10**9):
        """
        初始化Dgamewithpowers指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
    
    def case_generator(self):
        # 生成多样化的测试案例，包括边界值和不同范围的值
        if self.n_max <= 100:
            n = random.randint(self.n_min, self.n_max)
        else:
            # 30% 小值，30% 中等值，40% 大值
            rand_val = random.random()
            if rand_val < 0.3:
                n = random.randint(self.n_min, 100)
            elif rand_val < 0.6:
                n = random.randint(101, 10**5)
            else:
                n = random.randint(10**6, self.n_max)
        
        # 强制加入关键边界值
        if random.random() < 0.2:  # 20% 概率强制使用边界案例
            n = random.choice([1, 2, 8])
            n = min(max(n, self.n_min), self.n_max)
        
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""Vasya和Petya正在玩数字幂游戏。给定n={n}，规则如下：

1. 两人轮流选择数字（Vasya先手）
2. 选择x后，x及其所有正整数次幂将永久禁用
3. 无法选择的玩家败北

请确定最终获胜者，并将答案用[answer]标签包裹，例如：[answer]Vasya[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

