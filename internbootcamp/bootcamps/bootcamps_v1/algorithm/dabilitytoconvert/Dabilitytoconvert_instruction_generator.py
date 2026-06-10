import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DabilitytoconvertInstructionGenerator(BaseInstructionGenerator):
    """Dabilitytoconvert Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dabilitytoconvert指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 2)
        self.max_n = params.get('max_n', 100)  # 测试时采用较小范围
        self.max_k_length = params.get('max_k_length', 10)
        self.min_k_length = params.get('min_k_length', 1)
    
    def case_generator(self):
        for _ in range(1000):
            n = random.randint(self.min_n, self.max_n)
            allowed_digits = list(map(str, range(min(n, 10))))
            if not allowed_digits:
                allowed_digits = ['0']
            
            # 生成有效k_str（每个字符严格<n）
            k_length = random.randint(self.min_k_length, self.max_k_length)
            k_chars = [random.choice(allowed_digits) for _ in range(k_length)]
            k_str = ''.join(k_chars).lstrip('0') or '0'
            
            if len(k_str) > 60:
                continue
            
            # 计算正确答案
            try:
                expected_x = self.calculate_min_x(n, k_str)
                if expected_x is not None and 0 <= expected_x <= 1e18:
                    return {'n': n, 'k': k_str, 'expected_x': expected_x}
            except Exception as e:
                continue
        
        # 保底用例
        return {'n': 10, 'k': '0', 'expected_x': 0}
    
    @staticmethod
    def prompt_func(case):
        return f"""Alexander将十进制数转换为n进制时，用十进制数字代替字母。例如，当n=16时，475转换为'11311'。现在给定n={case['n']}和k={case['k']}，请找出最小的十进制数x，使得x转换为n进制的Alexander表示正好是k。答案请写在[answer]和[/answer]之间。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def calculate_min_x(self, n, k_str):
        INF = 10**19
        length = len(k_str)
        if length == 0:
            return 0

        # 预处理n的位数阈值
        tr = len(str(n))

        # 初始化权值数组
        pown = [1] * 70
        for i in range(1, 70):
            pown[i] = pown[i-1] * n if pown[i-1] <= INF // n else INF

        # DP表：dp[i][j] = (min_value, digits_count)
        dp = [[(INF, 0) for _ in range(length)] for __ in range(length)]

        # 填充DP表
        for l in range(1, length+1):
            for i in range(length - l + 1):
                j = i + l - 1
                current_str = k_str[i:j+1]

                # 候选1：整个子串作为单个数字
                if len(current_str) <= tr:
                    num = int(current_str)
                    if num < n and num < dp[i][j][0]:
                        dp[i][j] = (num, 1)

                # 候选2：分割子串
                for mid in range(i, j):
                    left_val, left_len = dp[i][mid]
                    right_val, right_len = dp[mid+1][j]
                    if right_len >= len(pown) or pown[right_len] == INF:
                        continue
                    combined = left_val * pown[right_len] + right_val
                    if combined < dp[i][j][0] and combined <= INF:
                        dp[i][j] = (combined, left_len + right_len)

        return dp[0][length-1][0] if dp[0][length-1][0] <= 1e18 else None
