import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CaddoneInstructionGenerator(BaseInstructionGenerator):
    """Caddone Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Caddone指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.params = params
    
    def case_generator(self):
        # 平衡生成随机和边界用例
        if random.random() < 0.2:  # 20%概率生成预定义边界用例
            cases = [
                (1912, 1), (5, 6), (999, 1),
                (88, 2), (12, 100), (1, 200000),
                (10**9, 1), (9, 200000), (0, 1)
            ]
            n, m = random.choice(cases)
        else:  # 80%概率生成随机有效用例
            n = random.randint(1, 10**9)
            m = random.randint(1, 2*10**5)
        
        # 确保n不包含前导零
        return {'n': n, 'm': m}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        return f"""Given initial number {n} and {m} operations where each digit d becomes the decimal representation of d+1:
(e.g. 9→10 becomes two digits). Compute the final number length modulo 10^9+7.

Rules:
1. Operations are applied simultaneously to all digits
2. 9→10, 5→6 (single-digit→single-digit)
3. Answer must be an integer within [answer]...[/answer] tags.

Example: For input 1912 with 1 operation:
[answer]5[/answer]

Now solve for n={n}, m={m}.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _precompute_mmap(cls):
        if cls._mmap is not None:
            return
        max_m = 2 * 10**5 + 10
        cls._mmap = [0] * (max_m + 10)  # 覆盖最大可能m+9的情况

        # 初始化状态：0应用0次操作时的位数
        cnts = [0] * 10
        cnts[0] = 1

        # 预处理所有可能的操作次数
        for k in range(0, max_m + 10):
            # 当前状态的总位数即为mmap[k]
            cls._mmap[k] = sum(cnts) % cls.MOD

            # 如果未达到最大次数，准备下一层状态
            if k >= max_m:
                continue

            # 更新下一层状态
            new_cnts = [0] * 10
            for d in range(10):
                next_num = d + 1
                for digit in str(next_num):
                    new_d = int(digit)
                    new_cnts[new_d] = (new_cnts[new_d] + cnts[d]) % cls.MOD
            cnts = new_cnts
