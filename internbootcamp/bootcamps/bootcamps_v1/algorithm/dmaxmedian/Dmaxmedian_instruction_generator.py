import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_max_median(n, k, array):
    """优化后的中位数计算函数"""
    left, right = min(array), max(array)
    answer = left  # 初始化
    
    while left <= right:
        mid = (left + right) // 2
        prefix = [0]*(n+1)
        min_prefix = float('inf')
        
        # 计算前缀和
        for i in range(n):
            prefix[i+1] = prefix[i] + (1 if array[i] >= mid else -1)
        
        # 寻找有效窗口
        valid = False
        for i in range(k, n+1):
            if prefix[i] - min_prefix > 0:
                valid = True
                break
            min_prefix = min(min_prefix, prefix[i - k + 1])
        
        if valid:
            answer = mid
            left = mid + 1
        else:
            right = mid - 1
    
    return answer


class DmaxmedianInstructionGenerator(BaseInstructionGenerator):
    """Dmaxmedian Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dmaxmedian指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        default_params = {
            'min_n': 5,
            'max_n': 20,
            'max_val': 20,
            'ensure_solvable': True  # 保证生成有解的案例
        }
        self.params = {**default_params, **params}
    
    def case_generator(self):
        """生成有效案例的优化版本"""
        n = random.randint(self.params['min_n'], self.params['max_n'])
        k = random.randint(1, n)
        
        # 生成有解数组的逻辑
        while True:
            arr = [random.randint(1, self.params['max_val']) for _ in range(n)]
            if len(set(arr)) >= 2:  # 确保至少有两个不同值
                break
        
        return {
            'n': n,
            'k': k,
            'array': arr.copy(),
            'answer': calculate_max_median(n, k, arr)
        }
    
    @staticmethod
    def prompt_func(case):
        return f"""给定长度为n的数组，请找出长度≥k的连续子数组的最大中位数。

输入：
{case['n']} {case['k']}
{' '.join(map(str, case['array']))}

规则：
1. 中位数定义：排序后第⌊(长度+1)/2⌋个元素
2. 子数组必须连续且长度≥k
3. 输出最大可能的中位数

请将最终答案放在[answer]标签内，如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

