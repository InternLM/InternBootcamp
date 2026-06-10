import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_case(n_input, k_input):
    MAX_PRECOMPUTE = 100
    f = [0]
    for _ in range(MAX_PRECOMPUTE):
        f.append(f[-1] * 4 + 1)
    p = [0]
    for g in range(MAX_PRECOMPUTE):
        p.append(p[-1] + (2 ** (g + 1) - 1))
    
    n, k = n_input, k_input

    if k == 1:
        return f"YES {n-1}"
    
    # 计算最大可能的分割次数（不考虑路径条件）
    max_f = (4**n - 1) // 3
    if k > max_f:
        return "NO"
    
    original_n = n
    
    # 直接遍历所有可能的j（不截断n）
    for j in range(original_n - 1, -1, -1):
        m_segment = original_n - j
        
        # 计算当前段的p值
        if m_segment < len(p):
            current_p = p[m_segment]
        else:
            current_p = 2 * (2**m_segment - 1) - m_segment
        
        if current_p > k:
            continue
        
        # 计算剩余可用分割次数
        other = 2 ** m_segment
        if j < len(f):
            f_j = f[j]
        else:
            f_j = (4**j - 1) // 3
        
        avail = (other - 1) ** 2 * f_j
        
        # 判断是否满足总分割次数
        if current_p + avail >= k:
            answer_m = original_n - m_segment
            return f"YES {answer_m}"
    
    return "NO"


class DolyaandmagicalsquareInstructionGenerator(BaseInstructionGenerator):
    """Dolyaandmagicalsquare Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dolyaandmagicalsquare指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.params = params
    
    def case_generator(self):
        # 生成平衡的测试案例，涵盖边界情况
        if random.random() < 0.5:
            # 生成有效案例（有解）
            n = random.randint(1, 20)
            max_f = (4**n - 1) // 3
            if max_f == 0:  # 防止n=0的情况
                n = 1
                max_f = 1
            k = random.randint(1, max_f)
        else:
            # 生成无效案例（无解）
            n = random.randint(1, 15)
            max_f = (4**n - 1) // 3
            k = random.randint(max_f + 1, max_f * 2)
        return {'n': n, 'k': k}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        return f"""给定初始2^{n}×2^{n}的正方形，请判断是否可以进行恰好{k}次分裂操作，使得存在一条从左下到右上的同尺寸方块路径。答案格式：[answer]YES x[/answer]或[answer]NO[/answer]，其中x为log2(边长)。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

