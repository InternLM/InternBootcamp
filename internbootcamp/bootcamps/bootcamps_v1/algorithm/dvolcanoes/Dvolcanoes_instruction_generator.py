import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DvolcanoesInstructionGenerator(BaseInstructionGenerator):
    """Dvolcanoes Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dvolcanoes指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 4)
        self.m = params.get('m', 2)
        self.volcanoes = params.get('volcanoes', [])
    
    def case_generator(self):
        n = self.n
        m = self.m
        volcanoes = self.volcanoes.copy()
        # 确保起点和终点没有火山
        if (1, 1) in volcanoes:
            volcanoes.remove((1, 1))
        if (n, n) in volcanoes:
            volcanoes.remove((n, n))
        # 生成足够的火山位置
        while len(volcanoes) < m:
            x = random.randint(1, n)
            y = random.randint(1, n)
            if (x, y) not in volcanoes and (x, y) != (1, 1) and (x, y) != (n, n):
                volcanoes.append((x, y))
        # 随机打乱火山的位置
        random.shuffle(volcanoes)
        # 返回案例
        return {
            'n': n,
            'm': m,
            'volcanoes': volcanoes[:m]
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        volcanoes = question_case['volcanoes']
        volcanoes_str = ', '.join(map(str, volcanoes))
        prompt = f"你是一名沙漠探险者，被困在一个{n}×{n}的沙漠中。你需要从起点(1,1)移动到终点({n},{n})，但只能向右或向下移动。某些格子有火山，无法进入。你的任务是找到从起点到终点的最短时间（每步1秒）。如果没有路径，输出-1。\n"
        prompt += f"输入的沙漠大小是{n}，有{m}个火山，分别位于：{volcanoes_str}。\n"
        prompt += "请输出从起点到终点所需的最短时间，或者-1表示没有路径。\n"
        prompt += "将答案放在[answer]标签中，例如：\n"
        prompt += "[answer]6[/answer]\n"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

