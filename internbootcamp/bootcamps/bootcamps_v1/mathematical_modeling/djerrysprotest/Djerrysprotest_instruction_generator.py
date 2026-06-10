import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_probability(n, a_list):
    a = {}
    for i in range(n-1):
        for j in range(i+1, n):
            x = abs(a_list[i] - a_list[j])
            a[x] = a.get(x, 0) + 1

    d = list(a.keys())
    b = [0] * 10005

    for i in range(len(d)):
        for j in range(i, len(d)):
            key_i = d[i]
            key_j = d[j]
            sum_key = key_i + key_j
            contribution = a[key_i] * a[key_j]
            if key_i != key_j:
                contribution *= 2
            if sum_key < len(b):
                b[sum_key] += contribution

    for i in range(1, len(b)):
        b[i] += b[i-1]

    ans = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s = abs(a_list[i] - a_list[j])
            if s - 1 >= 0 and s - 1 < len(b):
                ans += b[s - 1]

    den = (n * (n-1) // 2) ** 3
    return ans / den if den != 0 else 0.0

def is_close(a, b, rel_tol=1e-6, abs_tol=1e-6):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class DjerrysprotestInstructionGenerator(BaseInstructionGenerator):
    """Djerrysprotest Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, a_min=1, a_max=5000):
        """
        初始化Djerrysprotest指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        possible = list(range(self.a_min, self.a_max + 1))
        a = random.sample(possible, n)
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        problem = (
            "Andrew 和 Jerry 正在玩一个游戏，Harry 担任裁判。游戏进行三轮，每轮两人从罐子中随机抽取不同的球（球上有唯一正整数）。\n"
            "规则：\n"
            "1. 每轮两人抽球后，数字大者获胜，球放回罐子\n"
            "2. 先赢两轮者赢得比赛\n\n"
            f"当前罐中共有 {n} 个球，数字分别为：{', '.join(map(str, sorted(a)))}。\n"
            "已知 Andrew 赢了前两轮，Jerry 赢了第三轮。求 Jerry 三轮数字之和严格大于 Andrew 的概率。\n"
            "要求：答案保留至小数点后10位，误差不超过1e-6。将最终答案放在 [answer] 和 [/answer] 标签之间。\n"
            "示例：若答案为0.123456，则写为：[answer]0.1234560000[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

