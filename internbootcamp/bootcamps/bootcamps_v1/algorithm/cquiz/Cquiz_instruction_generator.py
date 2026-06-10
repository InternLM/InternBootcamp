import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 9


class CquizInstructionGenerator(BaseInstructionGenerator):
    """Cquiz Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cquiz指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数调整支持大范围数值生成
        """
        self.max_n = params.get('max_n', 10**12)  # 允许生成题目上限的千倍规模
        self.max_k = params.get('max_k', 10**12)
    
    def case_generator(self):
        # 确保覆盖k=2的边界情况
        k = random.choice([2] + [random.randint(2, min(self.max_k, 10**5)) for _ in range(4)])
        n = random.randint(k, min(self.max_n, 10**12))
        m = random.randint(0, n)

        # 正确性计算保持不变
        y = n % k
        x = n // k
        if m <= x * (k-1) + y:
            correct_ans = m % MOD
        else:
            z = m - (x * (k-1) + y)
            part1 = (pow(2, z+1, MOD) - 2) * k % MOD
            part2 = (m - z * k) % MOD
            correct_ans = (part1 + part2) % MOD
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'correct_ans': correct_ans
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # 保持原问题描述逻辑不变
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        return f"""你是算法竞赛专家，需要解决以下数学问题：

**问题描述**：
Manao参加了一个包含{n}个问题的测试。每个正确答案得1分并增加连续正确计数器。当计数器达到{k}时，得分会先加1分再翻倍，然后计数器重置。错误答案会重置计数器。已知Manao正确回答了{m}题，求可能的最小分数模1000000009的结果。

**输入参数**：
- 总题数 n = {n}
- 正确回答数 m = {m}
- 连续要求 k = {k}

**要求**：
1. 计算所有可能回答顺序中的最小分数
2. 答案必须模1000000009
3. 将最终答案放在[answer]和[/answer]标签之间

示例格式：[answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

