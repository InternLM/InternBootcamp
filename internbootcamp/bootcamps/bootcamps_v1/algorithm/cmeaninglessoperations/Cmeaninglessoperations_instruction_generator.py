import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CmeaninglessoperationsInstructionGenerator(BaseInstructionGenerator):
    """Cmeaninglessoperations Bootcamp指令生成器"""
    
    def __init__(self, all_ones_prob=0.5, min_k=2, max_k=25):
        """
        初始化Cmeaninglessoperations指令生成器
        
        Args:
            all_ones_prob: 参数描述
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Parameters:
            all_ones_prob: 生成全1二进制数的概率 (0-1)
            min_k: 最小二进制位数范围 (2-25)
            max_k: 最大二进制位数范围 (2-25)
        """
        self.all_ones_prob = min(max(all_ones_prob, 0.0), 1.0)
        self.min_k = max(2, min_k)
        self.max_k = min(25, max_k)
    
    def case_generator(self):
        """生成保证有效的测试用例"""
        if random.random() < self.all_ones_prob:
            # 生成全1二进制数 (格式: 2^k - 1)
            k = random.randint(self.min_k, self.max_k)
            return {"a": (1 << k) - 1}
        else:
            # 生成非全1数，确保至少有一个0位
            min_valid_k = max(self.min_k, 3)  # 保证k>=3才有非全1解
            k = random.randint(min_valid_k, self.max_k)
            
            # 生成有效范围内数字
            a_min = (1 << (k-1)) + 1
            a_max = (1 << k) - 2
            a = random.randint(a_min, a_max)
            
            # 二次验证数字有效性
            while bin(a).count('0') == 0 or a.bit_length() != k:
                a = random.randint(a_min, a_max)
            
            return {"a": a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case["a"]
        return f"""你需要解决一个基于位运算和最大公约数（GCD）的数学谜题。

给定正整数 a={a}，请找到一个整数 b（1 ≤ b < a），使得以下两个值的GCD最大：
1. a XOR b（按位异或）
2. a AND b（按位与）

请通过以下步骤解决：
1. 分析不同b值对应的计算结果
2. 找出使GCD最大的最优b值
3. 计算并返回最大GCD值

示例：
当a=5时，选择b=2：
- XOR: 5 ^ 2 = 7
- AND: 5 & 2 = 0
- GCD(7, 0) = 7

请将最终答案放在[answer]和[/answer]标签之间，例如：
[answer]7[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

