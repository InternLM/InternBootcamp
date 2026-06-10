import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import isclose




class DgameInstructionGenerator(BaseInstructionGenerator):
    """Dgame Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dgame指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 2)
        self.r = params.get('r', 0)
        # 验证n和r的范围
        if self.n < 1 or self.n > 18:
            raise ValueError("n must be between 1 and 18")
        if self.r < 0 or self.r > (2 ** 18):
            raise ValueError("r must be between 0 and 2^18")
    
    def case_generator(self):
        n = self.n
        r = self.r
        size = 2 ** n
        # 生成初始c数组，考虑边界情况
        initial_c = [random.randint(0, 10**9) for _ in range(size)]
        # 确保至少有一次修改，如果r>0
        updates = []
        for _ in range(r):
            z = random.randint(0, size - 1)
            g = random.randint(0, 10**9)
            updates.append((z, g))
        case = {
            'n': n,
            'initial_c': initial_c,
            'r': r,
            'updates': updates
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        initial_c = question_case['initial_c']
        r = question_case['r']
        prompt = (
            "Allen和Bessie正在玩一个数字游戏。游戏规则如下：\n"
            "游戏由一个函数f决定，f接受n个二进制变量，返回一个实数值。"
            "初始时，所有变量设为-1，每轮随机选择一个玩家设置一个变量为0或1。"
            "游戏目标是计算在每一轮修改后的期望值，输出r+1个结果，每个结果保留六位小数。\n"
            "初始函数值为："
        )
        prompt += f"{initial_c}\n"
        prompt += "每次修改操作如下：\n"
        for i, (z, g) in enumerate(question_case['updates'], 1):
            prompt += f"第{i}次修改：将f的值{z}修改为{g}\n"
        prompt += (
            "请输出每次修改后的期望值，每个值放在[answer]标签内，"
            "保留六位小数，例如：[answer]1.500000[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

