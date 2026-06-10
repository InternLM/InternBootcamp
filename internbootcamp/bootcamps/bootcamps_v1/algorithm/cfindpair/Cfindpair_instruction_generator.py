import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_kth_pair(n, k, array):
    vs = sorted(array)  # 确保排序逻辑正确
    p = k - 1
    lenvs = len(vs)
    
    # 处理极端情况
    if lenvs == 0: return (None, None)
    if lenvs == 1: return (vs[0], vs[0])
    
    # 主计算逻辑
    prow = p // lenvs
    vrow = vs[prow]
    
    # 寻找连续元素块边界
    prow0 = prow
    while prow0 > 0 and vs[prow0-1] == vrow:
        prow0 -= 1
    prow1 = prow + 1
    while prow1 < lenvs and vs[prow1] == vrow:
        prow1 += 1
    
    # 计算有效块尺寸
    block_size = prow1 - prow0
    block_start_index = prow0 * lenvs
    
    # 剩余位置计算
    remaining = p - block_start_index
    if remaining < 0:
        return (vs[p//lenvs], vs[p%lenvs])
    
    # 计算列位置
    col = remaining // block_size
    return (vrow, vs[col])


class CfindpairInstructionGenerator(BaseInstructionGenerator):
    """Cfindpair Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=5, min_val=-10, max_val=10):
        """
        初始化Cfindpair指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        array = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        max_k = n * n
        # 保证k不超过n^2
        k = random.randint(1, max_k)
        return {
            'n': n,
            'k': k,
            'array': array
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [
            f"{question_case['n']} {question_case['k']}",
            ' '.join(map(str, question_case['array']))
        ]
        input_str = '\n'.join(input_lines)
        prompt = f"""你正在解决一个关于数组有序对的编程问题。根据给定数组和整数k，找出所有可能的有序对按字典序排列后的第k个对。

**详细规则**：
1. 生成所有n²个有序对(ai, aj)，每个元素可重复使用
2. 按字典序排序：(p1,q1) < (p2,q2) 当且仅当 p1 < p2 或 (p1=p2且q1 < q2)
3. 输出排序后的第k个对（从1开始计数）

**输入格式**：
- 第一行两个整数n和k
- 第二行n个整数

**当前测试输入**：
{input_str}

请将最终答案用[answer]和[/answer]标签包裹，例如：[answer]2 3[/answer]。确保只包含答案数值，不要包含其他说明。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

