import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import random
import re




class DthebestvacationInstructionGenerator(BaseInstructionGenerator):
    """Dthebestvacation Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=5, d_min=1, d_max=5):
        """
        初始化Dthebestvacation指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            d_min: 参数描述
            d_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，配置生成谜题实例的参数范围。
        :param n_min: 月份数的最小值，默认为2
        :param n_max: 月份数的最大值，默认为5
        :param d_min: 每月天数的最小值，默认为1
        :param d_max: 每月天数的最大值，默认为5
        """
        self.n_min = n_min
        self.n_max = n_max
        self.d_min = d_min
        self.d_max = d_max
    
    def case_generator(self):
        """
        生成符合要求的谜题实例，确保输入合法且有解。
        返回包含n, x, d列表及正确答案的字典。
        """
        n = random.randint(self.n_min, self.n_max)
        d = [random.randint(self.d_min, self.d_max) for _ in range(n)]
        sum_d = sum(d)
        x = random.randint(1, sum_d)
        correct_answer = self.calculate_max_hugs(n, x, d)
        return {
            'n': n,
            'x': x,
            'd': d,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将谜题实例转换为详细的自然语言问题，明确规则和输入格式。
        """
        n = question_case['n']
        x = question_case['x']
        d = question_case['d']
        d_str = ' '.join(map(str, d))
        prompt = f"""你是一位计划去Naha探望Coronavirus-chan的旅行者，想要规划你的假期以获得最多的拥抱次数。以下是详细规则：

1. Naha的日历有{n}个月，每个月的天数分别为{d_str}。每年结束后，月份循环重复（即第n月之后是第1月）。
2. 你需要选择连续的{x}天作为假期。假期可以跨年，例如，从某一年的最后一个月延续到下一年的第一个月。
3. 在第i个月的第j天，你会得到j次拥抱。
4. 你的目标是找到这连续的{x}天，使得所有天的拥抱次数总和最大。

输入数据的第一行是两个整数n和x，第二行是n个整数表示每个月的天数。请根据这些输入，计算出最大可能的拥抱次数。

将答案放在[answer]和[/answer]标签之间，例如：[answer]42[/answer]。

示例输入：
3 2
1 3 1

示例输出：
5（对应的正确格式是[answer]5[/answer]）

现在，请解决以下问题：

输入：
{n} {x}
{d_str}

答案："""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_max_hugs(n_input, x_input, d_list):
        """
        根据参考代码逻辑计算最大拥抱数。
        """
        a = d_list.copy()
        a.extend(d_list)
        pa = [0]
        pb = [0]
        for day in a:
            pa.append(pa[-1] + day)
            pb.append(pb[-1] + (day * (day + 1)) // 2)
        k = x_input
        ans = 0
        for i in range(len(a)):
            target = pa[i] + k
            x = bisect.bisect_left(pa, target)
            if x > len(pa) - 1:
                continue
            total_hugs = pb[x] - pb[i]
            extra_days = pa[x] - pa[i] - k
            hh = (extra_days * (extra_days + 1)) // 2
            an = total_hugs - hh
            if an > ans:
                ans = an
        return ans
