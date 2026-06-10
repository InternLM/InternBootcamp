import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CnastyaandawardrobeInstructionGenerator(BaseInstructionGenerator):
    """Cnastyaandawardrobe Bootcamp指令生成器"""
    
    def __init__(self, x_min=0, x_max=10**18, k_min=0, k_max=10**18):
        """
        初始化Cnastyaandawardrobe指令生成器
        
        Args:
            x_min: 参数描述
            x_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 参数有效性校验
        if x_min < 0 or x_max > 10**18 or x_min > x_max:
            raise ValueError("Invalid x range: must satisfy 0 ≤ x_min ≤ x_max ≤ 1e18")
        if k_min < 0 or k_max > 10**18 or k_min > k_max:
            raise ValueError("Invalid k range: must satisfy 0 ≤ k_min ≤ k_max ≤ 1e18")

        self.x_min = x_min
        self.x_max = x_max
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        def generate_value(v_min, v_max, prefer_edge_prob=0.3):
            """增强版数值生成，确保：'''
            1. 正确生成极大数（兼容1e18）
            2. 优先生成边界值的概率
            3. 包含0的特殊处理"""
            edge_candidates = []
            if v_min == v_max:
                return v_min
            
            # 添加合法边界候选
            if v_min <= 0 <= v_max:
                edge_candidates.append(0)
            if v_max != 0 and v_max > 0:
                edge_candidates.append(v_max)
            
            # 添加典型候选值（如1等）
            if 1 > v_min and 1 < v_max:
                edge_candidates.append(1)
            
            # 概率选择边界值
            if edge_candidates and random.random() < prefer_edge_prob:
                return random.choice(edge_candidates)
            
            # 大数安全生成（Python的randint支持大整数）
            return random.randint(v_min, v_max)
        
        return {
            'x': generate_value(self.x_min, self.x_max),
            'k': generate_value(self.k_min, self.k_max)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        x = question_case['x']
        k_val = question_case['k']
        return f"""
Nastya的魔法衣柜问题解析

背景描述：
每个月初衣柜中的裙子数量会翻倍。在翻倍后（除最后一个月份外），衣柜有50%的概率吃掉1件裙子（如果当前有至少1件）。需要计算经过k+1个月后的期望裙子数量。

输入参数：
x = {x} (初始裙子数)
k = {k_val} (决定总月份数为k+1)

计算规则：
1. 当x=0时，结果直接为0
2. 否则使用公式：((2x-1) * 2^k + 1) mod (10^9+7)
3. 注意k=0时表示只经过1个月（不执行吃裙子操作）

示例验证：
输入 2 0 → 输出：4
输入 2 1 → 输出：7
输入 3 2 → 输出：21

请将最终答案放在[answer]标签内，例如：[answer]42[/answer]
当前题目参数：x={x}, k={k_val}
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

