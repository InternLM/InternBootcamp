import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ApbinaryInstructionGenerator(BaseInstructionGenerator):
    """Apbinary Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Apbinary指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'p_min': -1000,
            'p_max': 1000,
            'n_min': 1,
            'n_max': 10**9,
            'edge_case_prob': 0.2  # 20%生成边界案例
        }
        self.params.update(params)
    
    def case_generator(self):
        if random.random() < self.params['edge_case_prob']:
            return self._generate_edge_case()
        
        p = random.randint(self.params['p_min'], self.params['p_max'])
        n = random.randint(self.params['n_min'], self.params['n_max'])
        return {'n': n, 'p': p}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        p = question_case['p']
        prompt = f"""你是一个数学问题解决者，需要帮助解决一个关于p-binary数的特殊求和问题。给定两个整数n和p，找出能够组成n的最少数量的p-binary数，若不可能则返回-1。

**p-binary数**的定义为：2^x + p，其中x是非负整数。允许使用重复的p-binary数，并且允许和为负数的情况。

**输入参数**:
n = {n}
p = {p}

请确定所需的最少p-binary数的数量，并将答案放在[answer]标签内。例如：[answer]3[/answer]。

**示例**:
- 输入：n=24, p=0 → 输出：2（因为24=16+8=2^4+0 + 2^3+0）
- 输入：n=4, p=-7 → 输出：2（因为4= (16-7) + (2-7)）

请严格遵循输出格式，将最终答案放置在[answer]和[/answer]之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_edge_case(self):  # 修正：添加正确的缩进
        """生成边界测试案例"""
        edge_types = [
            {'p': 0},  # 常规二进制
            {'p': -1000, 'n': 10**9},  # 最小p值
            {'p': 1000, 'n': 1},       # 无解情况
            {'n': 1, 'p': 1},          # 样例5
            {'p': -1, 'n': 2**20 + 1}  # 大数值案例
        ]
        case = random.choice(edge_types)
        p = case.get('p', random.randint(-1000, 1000))
        n = case.get('n', random.randint(1, 10**9))
        return {'n': n, 'p': p}

    @staticmethod
    def solve(n, p):
        if p == 0:  # 优化常规二进制情况
            if (n & (n-1)) == 0:
                return 1
            return bin(n).count('1')

        max_i = 10**6 if p < 0 else min(10**6, n//abs(p)+2)
        for i in range(1, max_i+1):
            s = n - p * i
            if s <= 0:
                continue
            if s.bit_length() > 60:  # 处理极大数值溢出
                continue
            if bin(s).count('1') <= i and s >= i:
                return i
        return -1
