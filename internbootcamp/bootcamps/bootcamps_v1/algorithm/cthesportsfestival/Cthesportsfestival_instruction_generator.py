import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CthesportsfestivalInstructionGenerator(BaseInstructionGenerator):
    """Cthesportsfestival Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, s_min=1, s_max=10**9):
        """
        初始化Cthesportsfestival指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            s_min: 参数描述
            s_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max(max_n, min_n)
        self.s_min = s_min
        self.s_max = s_max
    
    def case_generator(self):
        # 多样化生成策略
        case_type = random.random()
        n = random.randint(self.min_n, self.max_n)
        
        if case_type < 0.2:  # 全同元素
            s = [random.randint(self.s_min, self.s_max)] * n
        elif case_type < 0.4:  # 递增序列
            base = random.randint(self.s_min, self.s_max//2)
            s = sorted([base + i*10 for i in range(n)])
        elif case_type < 0.6:  # 递减序列
            base = random.randint(self.s_min + n*10, self.s_max)
            s = sorted([base - i*10 for i in range(n)], reverse=True)
        else:  # 随机序列
            s = [random.randint(self.s_min, self.s_max) for _ in range(n)]
        
        sorted_s = sorted(s)
        
        # DP优化：滚动数组
        dp = [0] * n
        for r in range(n):
            new_dp = [0] * n
            for l in range(r, -1, -1):
                if l == r:
                    new_dp[l] = 0
                else:
                    new_dp[l] = sorted_s[r] - sorted_s[l] + min(dp[l+1], new_dp[l+1])
            dp = new_dp
        
        return {
            'n': n,
            's': s,
            'correct_sum': dp[0] if n > 0 else 0
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return (
            "作为学生会成员，你需要安排接力赛顺序使差异总和最小。差异d_i为前i人速度极差。\n\n"
            "输入格式：\n"
            f"{question_case['n']}\n{' '.join(map(str, question_case['s']))}\n\n"
            "将答案放入[answer]标签，如：[answer]123[/answer]。仅接受整数。"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

