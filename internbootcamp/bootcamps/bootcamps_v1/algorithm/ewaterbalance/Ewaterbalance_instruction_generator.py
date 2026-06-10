import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from decimal import Decimal
from decimal import getcontext

# === 源文件中的全局变量 ===

getcontext().prec = 20  # 设置高精度计算环境


class EwaterbalanceInstructionGenerator(BaseInstructionGenerator):
    """Ewaterbalance Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, min_val=1, max_val=20):
        """
        初始化Ewaterbalance指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        prompt = f"""你是解决水箱问题的专家，需要通过重新分配水量的操作得到字典序最小的序列。问题描述如下：

有{n}个水箱排成一行，初始水量分别为：{a}升。你可以多次进行以下操作：选择一个子段[l, r]，将该子段内的水量平均分配。例如，子段中所有水箱的水量会被替换为该子段的总水量的平均值。你的目标是找出通过任意次操作后，可能得到的字典序最小的序列。

字典序更小的定义是：比较两个序列，找到第一个不同的位置，该位置上数值较小的序列字典序更小。请确保你的答案在满足条件的情况下，每个数值的绝对或相对误差不超过1e-9。

输入格式：
第一行是一个整数n（1 ≤ n ≤ 1e6），表示水箱数量。
第二行是n个整数（1 ≤ a_i ≤ 1e6），表示初始水量。

输出格式：
输出n行，每行一个浮点数，表示最终各个水箱的水量，必须包含小数点后恰好9位（例如5.666666667）。

请将你的答案放置在[answer]和[/answer]标签之间，例如：

[answer]
5.666666667
5.666666667
5.666666667
7.000000000
[/answer]

现在，请解决当前问题，并按要求输出答案。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

