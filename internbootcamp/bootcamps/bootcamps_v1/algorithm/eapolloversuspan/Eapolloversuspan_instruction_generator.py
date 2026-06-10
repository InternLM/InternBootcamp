import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, array):
    if n == 0:
        return 0
    a = array
    b = [format(x, 'b')[::-1] for x in a]
    lens = [len(x) for x in b]
    maxK = max(lens) if lens else 0
    bcnt = [0] * maxK
    for i in range(n):
        x = b[i]
        for k in range(len(x)):
            if x[k] == '1':
                if k >= len(bcnt):
                    bcnt += [0] * (k - len(bcnt) + 1)
                bcnt[k] += 1
    kpowb = [ ((1 << k) % MOD) * bcnt[k] % MOD for k in range(len(bcnt)) ]
    summ = sum(kpowb) % MOD
    ans = 0
    for j in range(n):
        xj = a[j] % MOD
        x_bits = b[j]
        tmp = 0
        for k in range(len(x_bits)):
            if x_bits[k] == '1' and k < len(kpowb):
                tmp = (tmp + kpowb[k]) % MOD
        term_part = ( (xj * n) % MOD + (summ - tmp) % MOD ) % MOD
        term = (tmp * term_part) % MOD
        ans = (ans + term) % MOD
    return ans


class EapolloversuspanInstructionGenerator(BaseInstructionGenerator):
    """Eapolloversuspan Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=1000, max_x=10**18):
        """
        初始化Eapolloversuspan指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_x: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(1, min_n)
        self.max_n = min(max_n, 5*10**5)
        self.max_x = min(max_x, (1 << 60)-1)  # 确保不超过题目限制
    
    def case_generator(self):
        # 增加更多边界情况
        case_type = random.choice([0, 1, 2, 3])
        n = random.randint(self.min_n, self.max_n)
        
        if case_type == 0:  # 全零
            array = [0]*n
        elif case_type == 1:  # 全相同高位
            base = random.getrandbits(60)
            array = [base]*n
        elif case_type == 2:  # 混合高低位
            array = [random.getrandbits(random.randint(0, 60)) for _ in range(n)]
        else:  # 极大值
            array = [(1 << 60)-1 for _ in range(n)]
        
        return {"n": n, "array": array}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        array = question_case['array']
        case_input = f"1\n{n}\n{' '.join(map(str, array))}"
        problem_desc = (
            "数学挑战：计算三重位运算和\n\n"
            "给定长度为n的非负整数序列，计算：\n"
            "S = ΣΣΣ (x_i & x_j) * (x_j | x_k) mod 1e9+7 (i,j,k从1到n)\n\n"
            "输入格式：\n"
            "第一行t(测试用例数)\n"
            "每个用例两行：n和数组\n\n"
            "当前测试用例输入：\n"
            f"{case_input}\n\n"
            "将答案放在[answer]标签内，例如：[answer] 123 [/answer]"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

