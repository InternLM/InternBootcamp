import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import re
import random




class EarpaandagamewithmojtabaInstructionGenerator(BaseInstructionGenerator):
    """Earpaandagamewithmojtaba Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, max_num=10**9):
        """
        初始化Earpaandagamewithmojtaba指令生成器
        
        Args:
            max_n: 参数描述
            max_num: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_num = max_num
    
    def case_generator(self):
        case_type = random.choice([1, 2, 3, 4, 5])
        
        if case_type == 1:  # 全1的特殊测试样例
            n = random.randint(1, self.max_n)
            a = [1] * n
            
        elif case_type == 2:  # 单一素数不同次方
            primes = [2, 3, 5, 7, 11, 13, 17]
            p = random.choice(primes)
            n = random.randint(1, self.max_n)
            a = [p**random.randint(1, 5) for _ in range(n)]
            
        elif case_type == 3:  # 混合素数结构
            primes = random.sample([2, 3, 5, 7, 11, 13, 17], k=random.randint(2, 3))
            n = random.randint(2, self.max_n)
            a = [random.choice(primes)**random.randint(1, 4) for _ in range(n)]
            
        elif case_type == 4:  # 包含1的混合用例
            n = random.randint(2, self.max_n)
            k = random.randint(1, n-1)
            a = [1]*k + [random.choice([2,3,5,7])**random.randint(1,3) for _ in range(n-k)]
            
        else:  # 通用随机用例
            n = random.randint(1, self.max_n)
            a = [random.randint(1, self.max_num) for _ in range(n)]
            # 确保至少包含1个非1元素
            if all(x == 1 for x in a):
                a[random.randint(0, n-1)] = random.choice([2,3,5,7])

        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_str = f"{question_case['n']}\n{' '.join(map(str, question_case['a']))}"
        prompt = (
            "Mojtaba和Arpa正在玩一个数字游戏。规则如下：\n\n"
            "1. 玩家选择一个素数幂pk（p为素数，k≥1），该幂必须整除至少一个列表中的数\n"
            "2. 对于每个被pk整除的x，将其替换为x/pk\n"
            "3. 无法进行合法选择的玩家失败，Mojtaba先手\n\n"
            "请根据输入判断获胜者，将最终答案（Mojtaba或Arpa）放在[answer]和[/answer]标签之间。\n\n"
            f"输入：\n{input_str}\n\n"
            "输出格式示例：[answer]Arpa[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def prime_factors(n):
        if n == 1:
            return {}
        factors = {}
        while n % 2 == 0:
            factors[2] = factors.get(2, 0) + 1
            n //= 2
        i = 3
        while i*i <= n:
            while n % i == 0:
                factors[i] = factors.get(i, 0) + 1
                n //= i
            i += 2
        if n > 2:
            factors[n] = 1
        return factors

    @classmethod
    def _compute_sg(cls, state, memo):
        if state == 0:
            return 0
        if state in memo:
            return memo[state]

        mex = set()
        max_bit = state.bit_length()

        for i in range(max_bit):
            mask = 1 << i
            if state & mask:
                # 生成新状态：右移i+1位后与低位掩码组合
                new_state = (state >> (i+1)) | (state & ((1 << i) - 1))
                mex.add(cls._compute_sg(new_state, memo))

        res = 0
        while res in mex:
            res += 1
        memo[state] = res
        return res
