import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CteamInstructionGenerator(BaseInstructionGenerator):
    """Cteam Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_m=20):
        """
        初始化Cteam指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，确保生成的案例参数合法性
        """
        # 保证max_m至少为10以支持各种案例类型
        self.max_n = max(1, max_n)
        self.max_m = max(self.max_n*2+5, max_m)  # 动态调整保证案例生成可能性
    
    def case_generator(self):
        """
        严格遵循数学约束生成案例：
        1. 有解案例必须满足 n <= m+1 且 m <= 2(n+1)
        2. 无解案例必须违反上述任一条件
        """
        for _ in range(100):
            generate_solvable = random.choice([True, False])
            
            if generate_solvable:
                # 生成合法解的参数空间
                n = random.randint(1, self.max_n)
                m_lower = max(n-1, 1)
                m_upper = min(2*(n+1), self.max_m)
                
                if m_lower <= m_upper:
                    m = random.randint(m_lower, m_upper)
                    if n <= m+1 and m <= 2*(n+1):
                        return {'n': n, 'm': m}
                
            else:
                # 确保生成明确的非法参数组合
                violation_type = random.choice([1, 2])
                n, m = 0, 0
                
                if violation_type == 1:  # 违反条件1: n > m+1
                    while True:
                        m = random.randint(1, self.max_m)
                        min_n = m + 2
                        if min_n <= self.max_n:
                            n = random.randint(min_n, self.max_n)
                            break
                else:  # 违反条件2: m > 2(n+1)
                    while True:
                        n = random.randint(1, self.max_n)
                        min_m = 2*(n+1) + 1
                        if min_m <= self.max_m:
                            m = random.randint(min_m, self.max_m)
                            break
                
                # 最终验证参数组合的非法性
                if not (n <= m+1 and m <= 2*(n+1)):
                    return {'n': n, 'm': m}
        
        # 保底返回经典有解案例
        return {'n': 1, 'm': 2}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        生成包含完整规则和格式化要求的问题描述
        """
        n = question_case['n']
        m = question_case['m']
        return f"""作为编程奥林匹克选手，你需要解决以下卡牌排列问题：

给定{n}张0卡和{m}张1卡，要求排列满足：
1. 不能有相邻的两个0（如00非法）
2. 不能有超过两个连续1（如111非法）

请输出合法排列（如101）或-1表示无解。将最终答案包裹在[answer]标签内，如：[answer]1101[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

