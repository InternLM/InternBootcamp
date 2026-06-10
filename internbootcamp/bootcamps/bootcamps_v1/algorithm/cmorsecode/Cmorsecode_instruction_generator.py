import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

INVALID_4 = {"0011", "0101", "1110", "1111"}


class CmorsecodeInstructionGenerator(BaseInstructionGenerator):
    """Cmorsecode Bootcamp指令生成器"""
    
    def __init__(self, m_max=3000):
        """
        初始化Cmorsecode指令生成器
        
        Args:
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()  # 添加父类初始化
        self.m_max = m_max
    
    def case_generator(self):
        m = random.randint(1, self.m_max)
        operations = [random.choice(['0', '1']) for _ in range(m)]
        S = ''.join(operations)
        
        # 动态规划计算正确结果
        dp = [0] * (m + 1)
        dp[0] = 1  # 空序列的初始化值
        sum_so_far = 0
        expected_outputs = []
        
        for k in range(1, m + 1):
            current = 0
            for l in range(1, 5):
                if k >= l:
                    start = k - l
                    substring = S[start:k]
                    # 检查4字符的无效情况
                    if l == 4 and substring in INVALID_4:
                        continue
                    current += dp[start]
                    current %= MOD
            dp[k] = current % MOD
            sum_so_far = (sum_so_far + dp[k]) % MOD
            expected_outputs.append(sum_so_far)
        
        return {
            'm': m,
            'operations': operations,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        ops = question_case['operations']
        input_str = f"{m}\n" + '\n'.join(ops)
        return f"""Given a sequence of Morse code operations, calculate the valid letter sequences after each step. Each letter is represented by a Morse string (0: dot, 1: dash) of length 1-4, excluding the forbidden patterns: 0011, 0101, 1110, 1111.

Input format:
{input_str}

Output {m} lines with the count modulo 1e9+7 after each step. Enclose your final answers within [answer] tags:

Example:
[answer]
42
[/answer]

[answer]
""" + "\n".join(map(str, question_case['expected_outputs'])) + "\n[/answer]" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

