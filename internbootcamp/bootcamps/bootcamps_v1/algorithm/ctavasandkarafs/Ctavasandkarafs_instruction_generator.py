import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_r(A, B, l, t, m):
    v = A + (l - 1) * B
    if v > t:
        return -1

    lo, hi = 0, 10**8
    while lo < hi:
        mid = (lo + hi + 1) // 2
        sum_condition = (v + v + (mid - 1) * B) * mid
        right = t * min(m, mid) * 2
        if sum_condition > right:
            hi = mid - 1
        else:
            lo = mid

    if lo == 0:
        return -1

    max_r1 = l + lo - 1
    max_r2 = (t - A) // B + 1 if B != 0 else t
    r = min(max_r1, max_r2)
    return r if r >= l else -1


class CtavasandkarafsInstructionGenerator(BaseInstructionGenerator):
    """Ctavasandkarafs Bootcamp指令生成器"""
    
    def __init__(self, A=None, B=None, **params):
        """
        初始化Ctavasandkarafs指令生成器
        
        Args:
            A: 参数描述
            B: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        # 调整参数范围，生成更合理的测试案例
        self.A = A if A is not None else random.randint(1, 100)
        self.B = B if B is not None else random.randint(1, 100)
    
    def case_generator(self):
        # 控制参数范围以提高案例质量
        for _ in range(100):  # 防止无限循环
            l = random.randint(1, 50)
            s_l = self.A + (l-1)*self.B
            
            # 有50%概率生成有解案例
            if random.random() < 0.5:
                t = random.randint(s_l, s_l + 1000)
            else:
                t = random.randint(1, max(1, s_l - 1))
            
            m = random.randint(1, 100)
            expected_r = compute_r(self.A, self.B, l, t, m)
            
            # 确保生成的案例格式正确
            if expected_r != -1 or random.random() < 0.3:  # 保留部分无解案例
                return {
                    'A': self.A,
                    'B': self.B,
                    'l': l,
                    't': t,
                    'm': m,
                    'expected_r': expected_r
                }
        
        # 保底返回一个无解案例
        l = random.randint(1, 50)
        return {
            'A': self.A,
            'B': self.B,
            'l': l,
            't': random.randint(1, 10),
            'm': random.randint(1, 10),
            'expected_r': -1
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        A = question_case['A']
        B = question_case['B']
        l = question_case['l']
        t = question_case['t']
        m = question_case['m']
        prompt = f"""你正在帮助SaDDas解决关于Ctavasandkarafs的查询问题。Ctavasandkarafs按照无限序列排列，第i个的高度为s_i = {A} + (i-1) × {B}。每次操作（m-bite）可以选择最多m个不同的未被吃掉的Ctavasandkarafs，每个减少1点高度。当一个Ctavasandkarafs的高度变为0时被吃掉，无法再被选择。

给定查询参数：起始位置l={l}，最多允许t={t}次操作，每次操作最多选m={m}个Ctavasandkarafs。请找出最大的r满足以下条件：

1. l ≤ r；
2. 通过最多t次m-bite操作可以吃完第l到第r的所有Ctavasandkarafs。

如果不存在这样的r，请输出-1。答案必须是整数，格式为[answer]答案[/answer]，例如：[answer]5[/answer]或[answer]-1[/answer]。

当前问题参数：
A = {A}
B = {B}
l = {l}
t = {t}
m = {m}

注意：
1. 最终答案必须满足：max(s_l,...,s_r) ≤ t 且总操作次数足够
2. 答案只能放在[answer]标签内，其他位置将无法识别"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

