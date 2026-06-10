import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
from random import randint
import re




class CsequencepairweightInstructionGenerator(BaseInstructionGenerator):
    """Csequencepairweight Bootcamp指令生成器"""
    
    def __init__(self, max_t=2, max_n=5, a_max=5):
        """
        初始化Csequencepairweight指令生成器
        
        Args:
            max_t: 参数描述
            max_n: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_t = max_t
        self.max_n = max_n
        self.a_max = a_max  # 控制元素的范围
    
    def case_generator(self):
        t = randint(1, self.max_t)
        cases = []
        for _ in range(t):
            n = randint(1, self.max_n)
            a = [randint(1, self.a_max) for _ in range(n)]
            output = self._calculate_single_case(n, a)
            cases.append({
                'n': n,
                'a': a,
                'output': output
            })
        identity = {
            't': t,
            'cases': cases
        }
        return identity
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['t'])]
        for case in question_case['cases']:
            input_lines.append(str(case['n']))
            input_lines.append(' '.join(map(str, case['a'])))
        input_str = '\n'.join(input_lines)
        prompt = f"""你是编程竞赛的参赛者，请解决以下问题：

问题描述：

给定多个测试用例，每个测试用例要求计算数组所有子段的权重总和。权重定义为子段中相同值的无序对（i, j）的数量（i < j 并且a_i等于a_j）。子段是原数组的连续子序列。

输入格式：

输入的第一行是测试用例数目t。每个测试用例包含两行：第一行是整数n（数组长度），第二行是n个整数a_1到a_n。

输出格式：

对每个测试用例，输出一个整数，表示所有子段的权重总和。

示例：

输入：
2
4
1 2 1 1
4
1 2 3 4

输出：
6
0

现在，请解决以下输入中的测试用例：

输入：
{input_str}

请将答案放入[answer]标签内，每个测试用例的结果各占一行。例如：

[answer]
答案1
答案2
[/answer]

请确保您的答案正确且格式正确。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_single_case(n, a):
        s = defaultdict(int)
        ans = 0
        for i, x in enumerate(a):
            ans += s[x] * (n - i)
            s[x] += (i + 1)
        return ans
