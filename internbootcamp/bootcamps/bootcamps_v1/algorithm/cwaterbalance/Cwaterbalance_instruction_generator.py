import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_water_tanks(input_list):
    n = len(input_list)
    if n == 0:
        return []
    l = input_list
    su = [l[0]]
    cou = [-1, 0]
    for k in range(1, n):
        nd = 1
        ns = l[k]
        while len(cou) > 1 and su[-1] * (cou[-1] - cou[-2] + nd) > (su[-1] + ns) * (cou[-1] - cou[-2]):
            nd += cou[-1] - cou[-2]
            ns += su[-1]
            su.pop()
            cou.pop()
        cou.append(k)
        su.append(ns)
    af = []
    for k in range(len(su)):
        count = cou[k+1] - cou[k]
        avg = su[k] / count
        af.extend([avg] * count)
    return af


class CwaterbalanceInstructionGenerator(BaseInstructionGenerator):
    """Cwaterbalance Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=15, min_val=1, max_val=100):
        """
        初始化Cwaterbalance指令生成器
        
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
        input_list = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        output = solve_water_tanks(input_list)
        return {
            'input': input_list,
            'output': output
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_list = question_case['input']
        n = len(input_list)
        input_str = ' '.join(map(str, input_list))
        prompt = f"""你是一个编程竞赛选手，正在解决一个关于水箱水量优化的问题。请根据题目描述，找到字典序最小的可能序列。

题目描述：

有n个水箱排成一行，第i个水箱初始有a_i升水。你可以进行任意次数的操作：选择一个子段[l, r]，将该区域内的水重新分配，使得每个水箱中的水等于该子段的总水量除以区间长度。例如，初始为[1,3,6,7]，选择子段[2,3]，得到[1,4.5,4.5,7]。你的任务是找到可以通过这些操作得到的字典序最小的水量序列。

字典序定义的补充说明：两个序列从左到右比较第一个不同的元素，较小的元素所在的序列更小。

输入格式：

第一行为整数n，第二行包含n个整数a_1到a_n。

输出格式：

输出n行，每行精确到九位小数，格式为X.XXXXXXXXX（如5.666666667或7.000000000）。

请根据以下输入数据计算答案，并将最终结果按指定格式放在[answer]和[/answer]之间。

输入数据：
n = {n}
初始水量 = {input_str}

请按照以下格式输出答案：
[answer]
值1.xxxxxxxxx
值2.xxxxxxxxx
...
值n.xxxxxxxxx
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

