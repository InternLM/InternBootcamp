import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DbookshelvesInstructionGenerator(BaseInstructionGenerator):
    """Dbookshelves Bootcamp指令生成器"""
    
    def __init__(self, max_n=50, max_book_value=(1 << 50)-1):
        """
        初始化Dbookshelves指令生成器
        
        Args:
            max_n: 参数描述
            max_book_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_book_value = max_book_value
    
    def case_generator(self):
        """生成完全随机且符合题目约束的测试用例"""
        while True:  # 确保至少存在有效分割
            n = random.randint(1, self.max_n)
            k = random.randint(1, n)
            a = [random.randint(1, self.max_book_value-1) for _ in range(n)]
            if self.validate_case(n, k, a):
                return {"n": n, "k": k, "a": a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        k = question_case["k"]
        a = question_case["a"]
        return f"""## 书架美丽值最大化问题

Mr. Keks需要将{n}本价格分别为{a}的书分配到{k}个连续的书架上。每个书架必须包含至少一本书，书架的价值是其上所有书的价格之和。总美丽值是所有书架价值的按位与运算结果。

**任务**：找出能获得最大美丽值的分法。

**输出要求**：将最终答案包裹在[answer]标签中，例如：[answer]42[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def validate_case(self, n, k, a):
        """验证生成的案例至少存在一个有效分割"""
        try:
            self.compute_max_beauty(n, k, a)
            return True
        except:
            return False

    @staticmethod
    def compute_max_beauty(n, k, a):
        """优化后的正确性验证算法"""
        prefix = [0] * (n + 1)
        for i in range(n):
            prefix[i+1] = prefix[i] + a[i]

        result = 0
        for bit in reversed(range(61)):
            mask = result | (1 << bit)
            dp = [False] * (n + 1)
            dp[0] = True

            for _ in range(k):
                new_dp = [False] * (n + 1)
                for end in range(n+1):
                    if not dp[end]: continue
                    for new_end in range(end+1, n+1):
                        if (prefix[new_end] - prefix[end]) & mask == mask:
                            new_dp[new_end] = True
                dp = new_dp

            if dp[n]:
                result = mask
        return result
