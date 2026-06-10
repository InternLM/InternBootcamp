import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CbunsInstructionGenerator(BaseInstructionGenerator):
    """Cbuns Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=1000, m_min=1, m_max=10, stuffing_min=1, stuffing_max=100):
        """
        初始化Cbuns指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
            stuffing_min: 参数描述
            stuffing_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
        self.stuffing_min = stuffing_min
        self.stuffing_max = stuffing_max
    
    def case_generator(self):
        """生成完全符合题目约束的合法案例"""
        m = random.randint(self.m_min, self.m_max)
        n = random.randint(max(self.n_min, 1), self.n_max)  # 确保n≥1
        
        # 保证c0/d0的取值满足1 ≤ c0,d0 ≤ 100
        c0 = random.randint(max(self.stuffing_min, 1), min(self.stuffing_max, 100))
        d0 = random.randint(max(self.stuffing_min, 1), min(self.stuffing_max, 100))
        
        stuffings = []
        for _ in range(m):
            # 保证所有参数满足1 ≤ ai,bi,ci,di ≤100
            ai = random.randint(1, 100)
            bi = random.randint(1, 100)
            ci = random.randint(1, 100)
            di = random.randint(1, 100)
            # 确保bi≥1避免除零错误
            bi = max(1, bi)
            stuffings.append((ai, bi, ci, di))
        
        return {
            'n': n,
            'm': m,
            'c0': c0,
            'd0': d0,
            'stuffings': stuffings
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['c0']} {question_case['d0']}"
        ]
        for stuffing in question_case['stuffings']:
            input_lines.append(" ".join(map(str, stuffing)))
        
        return (
            "Lavrenty需要制作包子获取最大利润，规则如下：\n"
            "1. 总共有n克面团和m种馅料\n"
            "2. 无馅包子消耗c0克面团，利润d0\n"
            "3. 第i种馅料的参数：可用ai克，每个包子需要bi克馅料和ci克面团，利润di\n"
            "4. 输出最大利润\n\n"
            "输入数据：\n" + "\n".join(input_lines) +
            "\n\n将最终答案放在[answer]和[/answer]之间"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_correct_answer(cls, identity):
        """优化后的答案计算逻辑"""
        n = identity['n']
        m = identity['m']
        c0 = identity['c0']
        d0 = identity['d0']
        stuffings = identity['stuffings']

        # 合并所有包子类型（0为无馅，1~m为有馅）
        items = [(c0, d0, float('inf'))]  # (ci, di, 最大数量)
        for ai, bi, ci, di in stuffings:
            max_count = ai // bi
            items.append((ci, di, max_count))

        # 背包DP优化实现
        dp = [0] * (n + 1)
        for ci, di, max_count in items:
            for j in range(n, ci-1, -1):
                max_k = min(max_count, j // ci)
                dp[j] = max(dp[j - k*ci] + k*di for k in range(0, max_k+1))

        return max(dp)
