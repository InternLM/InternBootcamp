import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpredictoutcomeofthegameInstructionGenerator(BaseInstructionGenerator):
    """Cpredictoutcomeofthegame Bootcamp指令生成器"""
    
    def __init__(self, min_m=1, max_m=10**4):
        """
        初始化Cpredictoutcomeofthegame指令生成器
        
        Args:
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数控制最终胜利数m的范围（总比赛数n=3m）
        """
        super().__init__()
        self.min_m = max(1, min_m)
        self.max_m = max_m
    
    def case_generator(self):
        # 生成必然有解的案例（yes案例）
        m = random.randint(self.min_m, self.max_m)
        n = 3 * m
        
        # 在[0, m]范围内生成x,y,z，总和不超过k_max（最大不超过n）
        # k可以在0到n之间，但需要满足x+y+z=k且x,y,z <=m
        x = random.randint(0, m)
        y = random.randint(0, m)
        z = random.randint(0, m)
        k = x + y + z  # 确保k <=3m =n
        
        # 避免k超过n的情况
        if k > n:
            k = n
            x = min(x, m)
            y = min(y, m)
            z = k -x -y
            z = max(0, min(z, m))
        
        d1 = abs(x - y)
        d2 = abs(y - z)
        
        # 生成包含有效解的案例
        return {
            'n': n,
            'k': k,
            'd1': d1,
            'd2': d2,
            '_expected': 'yes'  # 标记预期答案
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        problem = (
            "作为足球锦标赛观察员，判断是否存在以下条件满足的情况：\n"
            f"- 总比赛数：{case['n']}\n"
            f"- 已进行比赛：{case['k']}\n"
            f"- 队伍1与2胜利差：{case['d1']}\n"
            f"- 队伍2与3胜利差：{case['d2']}\n"
            "规则：所有比赛必须分出胜负，最终三队胜利数完全相同。\n"
            "答案用[answer]标签包裹，例如：[answer]yes[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n, k, d1, d2):
        if n % 3 != 0:
            return False
        m = n // 3
        signs = [(1,1), (1,-1), (-1,1), (-1,-1)]
        for s1, s2 in signs:
            adjusted_d1 = s1 * d1
            adjusted_d2 = s2 * d2
            x = (k + 2*adjusted_d1 + adjusted_d2)
            if x < 0 or x % 3 != 0:
                continue
            x = x // 3
            y = (k + adjusted_d1 + adjusted_d2) - 2*x
            if y < 0 or (y + x) < adjusted_d1:
                continue
            z = x - adjusted_d1 - adjusted_d2
            if z < 0:
                continue
            if (x + y + z) != k:
                continue
            if m >= x and m >= y and m >= z:
                return True
        return False
