import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CpalindromicpathsInstructionGenerator(BaseInstructionGenerator):
    """Cpalindromicpaths Bootcamp指令生成器"""
    
    def __init__(self, n=3):
        """
        初始化Cpalindromicpaths指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if (n % 2) == 0:
            n += 1  # 确保n为奇数
        self.n = n
    
    def case_generator(self):
        n = self.n
        grid = [[0] * n for _ in range(n)]
        grid[0][0] = 1  # 左上角为1
        grid[-1][-1] = 0  # 右下角为0
        
        # 随机生成其他单元格的值
        for i in range(n):
            for j in range(n):
                if i == 0 and j == 0:
                    continue
                if i == n-1 and j == n-1:
                    continue
                grid[i][j] = random.choice([0, 1])
        
        return {
            'n': n,
            'grid': grid
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        grid = question_case['grid']
        example = "\n".join(["".join(map(str, row)) for row in grid])
        
        prompt = f"你有一个{n}×{n}的网格。已知左上角（1,1）的值是1，右下角（{n},{n}）的值是0。其他单元格的值是0或1。你需要通过询问问题来确定整个网格的值。每次询问的形式是“? x1 y1 x2 y2”，并得到0或1的回答。你的任务是输出整个网格的值，每行是一个由0和1组成的字符串，例如：\n\n"
        prompt += f"示例网格：\n{example}\n\n"
        prompt += "请将答案放在[answer]标签中，格式如下：\n"
        prompt += "[answer]\n"
        prompt += "100\n"
        prompt += "001\n"
        prompt += "000\n"
        prompt += "[/answer]\n"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

