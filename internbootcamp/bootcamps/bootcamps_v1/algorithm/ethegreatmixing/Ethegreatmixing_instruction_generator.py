import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from itertools import combinations

# === 源文件中的全局函数 ===

def solve_case(n, c):
    if n in c:
        return 1
    q = {cc - n for cc in c}
    max_q = max(q)
    min_q = min(q)
    if max_q < 0 or min_q > 0:
        return -1
    max_positive = max_q
    min_negative_abs = -min_q
    maxs = [3000] * (max_positive + 1)
    mins = [3000] * (min_negative_abs + 1)
    for qq in q:
        if qq > 0 and qq <= max_positive:
            maxs[qq] = 1
        elif qq < 0:
            idx = -qq
            if idx <= min_negative_abs:
                mins[idx] = 1
    ans = float('inf')
    mni = len(mins) - 1
    mxi = len(maxs) - 1
    while mni > 0 and mxi > 0:
        if mni > mxi:
            mni, mxi = mxi, mni
            mins, maxs = maxs, mins
        for i in range(mni, 0, -1):
            if mxi - i >= 0:
                maxs[mxi - i] = min(maxs[mxi - i], maxs[mxi] + mins[i])
        mxi -= 1
        while mxi > 0 and maxs[mxi] > 2500:
            mxi -= 1
    final_min = min(maxs[0], mins[0])
    return final_min if final_min <= 2500 else -1


class EthegreatmixingInstructionGenerator(BaseInstructionGenerator):
    """Ethegreatmixing Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ethegreatmixing指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': 0,
            'max_n': 1000,
            'min_k': 1,
            'max_k': 1000,  # 允许大k值输入
            'case_type': 'mixed'  # 可配置案例类型: simple/complex/mixed
        }
        self.params.update(params)
    
    def case_generator(self):
        params = self.params
        while True:
            n = random.randint(params['min_n'], params['max_n'])
            k = random.randint(params['min_k'], params['max_k'])
            
            # 处理边界情况
            if n == 0 or n == 1000:
                a = [n] * k  # 边界情况必须包含目标值
            else:
                # 根据配置生成不同类型的案例
                case_strategy = random.choice(['simple', 'complex']) \
                    if params['case_type'] == 'mixed' else params['case_type']
                
                if case_strategy == 'simple':
                    # 生成必含目标值的简单案例
                    a = [n]
                    a += [random.randint(0, 1000) for _ in range(k-1)]
                else:
                    # 生成需要混合的复杂案例
                    a = []
                    attempt = 0
                    valid = False
                    while not valid and attempt < 100:
                        attempt += 1
                        a = []
                        # 添加正负差值元素各至少一个
                        a.append(random.randint(n+1, 1000))
                        a.append(random.randint(0, n-1))
                        # 填充剩余元素
                        a += [random.randint(0, 1000) for _ in range(k-2)]
                        # 确保不包含目标值
                        if n in a: continue
                        # 检查是否存在有效解
                        if solve_case(n, a) != -1:
                            valid = True
                    if not valid:
                        continue
            # 确保长度正确
            a = a[:k]
            # 验证答案有效性
            ans = solve_case(n, a)
            if ans != -1:
                return {'n': n, 'k': k, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        k = question_case['k']
        problem_desc = (
            f"调配目标浓度：{n}%，现有{len(a)}种可乐浓度：{', '.join(map(str, a))}\n"
            "规则：混合整数升可乐使浓度恰好等于目标值，求最小总升数\n"
            "注意：若无解需返回-1，答案格式示例：[answer]3[/answer]"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

