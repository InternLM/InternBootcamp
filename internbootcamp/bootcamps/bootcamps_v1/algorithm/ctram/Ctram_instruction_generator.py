import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtramInstructionGenerator(BaseInstructionGenerator):
    """Ctram Bootcamp指令生成器"""
    
    def __init__(self, s_min=2, s_max=1000, t_min=1, t_max=1000):
        """
        初始化Ctram指令生成器
        
        Args:
            s_min: 参数描述
            s_max: 参数描述
            t_min: 参数描述
            t_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.s_min = s_min
        self.s_max = s_max
        self.t_min = t_min
        self.t_max = t_max
        super().__init__()
    
    def case_generator(self):
        s = random.randint(self.s_min, self.s_max)
        x1 = random.randint(0, s)
        x2 = random.randint(0, s)
        while x2 == x1:
            x2 = random.randint(0, s)
        t1 = random.randint(self.t_min, self.t_max)
        t2 = random.randint(self.t_min, self.t_max)
        p = random.randint(1, s-1)
        d = random.choice([1, -1])
        return {
            's': s,
            'x1': x1,
            'x2': x2,
            't1': t1,
            't2': t2,
            'p': p,
            'd': d
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        x1 = question_case['x1']
        x2 = question_case['x2']
        t1 = question_case['t1']
        t2 = question_case['t2']
        p = question_case['p']
        d = question_case['d']
        direction_desc = "正向（从0到s）" if d == 1 else "负向（从s到0）"
        prompt = f"""Igor需要从坐标{x1}前往坐标{x2}。有轨电车在0到{s}米的直线上往返行驶，每移动1米需要{t1}秒。当前时刻，电车位于坐标{p}，并正在以{direction_desc}行驶。电车在到达0或{s}后会立即掉头，保持匀速运动。

Igor的步行速度为每米{t2}秒。他可以在任何与电车位置重合的时刻上下车，上下车时间不计。请计算Igor到达目的地所需的最短时间（单位：秒）。

请将最终答案放入[answer]标签内，例如：[answer]8[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

