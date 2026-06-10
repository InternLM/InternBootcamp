import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CwonderfulrandomizedsumInstructionGenerator(BaseInstructionGenerator):
    """Cwonderfulrandomizedsum Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, min_val=-10000, max_val=10000):
        """
        初始化Cwonderfulrandomizedsum指令生成器
        
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
        arr = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        return {
            "n": n,
            "array": arr
        }
    
    @staticmethod
    def prompt_func(question_case):
        arr = question_case["array"]
        arr_str = ' '.join(map(str, arr))
        problem_desc = f"""Valera需要解决一个数学问题，请你帮他计算出最大的总和。题目规则如下：

给定一个整数序列，你需要依次进行两个操作：
1. 选择一个前缀（从第一个元素开始的一段连续元素，可以为空），将该前缀中的每个元素乘以-1。
2. 选择一个后缀（从最后一个元素开始的一段连续元素，可以为空），同样乘以-1。

这两个操作的前缀和后缀可以任意相交。你的目标是使得操作后的序列总和尽可能大。请计算出这个最大的可能总和。

输入序列为：
{arr_str}

请将计算得到的整数答案放置在[answer]和[/answer]标签之间，例如：[answer]42[/answer]。"""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

