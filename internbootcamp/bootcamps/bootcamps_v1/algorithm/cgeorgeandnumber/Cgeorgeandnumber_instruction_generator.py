import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CgeorgeandnumberInstructionGenerator(BaseInstructionGenerator):
    """Cgeorgeandnumber Bootcamp指令生成器"""
    
    def __init__(self, max_p_length=20):
        """
        初始化Cgeorgeandnumber指令生成器
        
        Args:
            max_p_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数，限制生成p的最大长度以避免计算过载
        :param max_p_length: p的最大长度，默认20位
        """
        self.max_p_length = max_p_length
    
    def case_generator(self):
        """
        生成有效案例的核心逻辑：先构造分解路径，再反向生成p
        """
        # 随机生成初始元素数量（至少1个）
        original_n = random.randint(1, 10)  # 控制原始数组大小避免指数爆炸
        
        # 生成模拟合并路径
        elements = [str(random.randint(1, 999)) for _ in range(original_n)]
        while len(elements) > 1:
            # 随机选择两个不同元素
            i, j = random.sample(range(len(elements)), 2)
            a, b = elements[i], elements[j]
            if int(a) < int(b):
                a, b = b, a  # 保证a >= b
            merged = a + b
            # 移除原元素并添加新元素
            elements = [e for idx, e in enumerate(elements) if idx not in {i,j}] + [merged]
        p = elements[0]
        
        # 根据参考代码逆向计算正确答案n
        ans = 0
        tem = []
        for i in range(len(p)-1, -1, -1):
            tem.append(p[i])
            if p[i] != '0':
                ans += 1
                cur = ''.join(tem[::-1])
                tem = []
                if (len(cur) > i and i) or (len(cur) == i and p[:i] < cur):
                    break
        
        return {'p': p, 'n': ans}
    
    @staticmethod
    def prompt_func(question_case):
        p = question_case['p']
        return f"""# 谜题描述

George的数组游戏规则：

1. 初始数组包含若干正整数
2. 每次操作：
   - 选择两个不同元素bi ≥ bj
   - 拼接生成新数v = concat(bi, bj)（如concat(500, 10)=50010）
   - 将v加入数组并移除bi和bj
3. 最终数组只剩一个数{p}

请计算初始数组可能的最大元素数量，将答案用[answer]标签包裹。例如：答案为4则写[answer]4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

