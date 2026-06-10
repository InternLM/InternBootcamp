import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DromandigitsInstructionGenerator(BaseInstructionGenerator):
    """Dromandigits Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**9):
        """
        初始化Dromandigits指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数，确保合理的数值范围
        """
        self.min_n = max(1, min_n)
        self.max_n = max(self.min_n, max_n)  # 修正参数校验逻辑
    
    def case_generator(self):
        """
        生成包含不同特征的测试用例：
        - 小数值（覆盖示例范围）
        - 临界值（n=11,12）
        - 大数值（超过12的随机数）
        """
        # 20%概率生成示例数值
        if random.random() < 0.2:
            return {'n': random.choice([1, 2, 10, 11, 12])}
        # 80%概率生成随机数值
        return {'n': random.randint(self.min_n, self.max_n)}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        return f"""你是一位罗马数字系统专家，请解答以下数学问题：

我们定义一种特殊的数值系统，使用四个罗马字符：
I(1), V(5), X(10), L(50)
数值计算规则为字符对应值的简单相加（忽略传统的位置规则），例如：
- IX → 1+10=11
- VL → 5+50=55
- XX → 10+10=20

问题：当恰好使用{n}个上述字符时，可以表示多少个不同的整数值？

注意事项：
1. 必须使用恰好{n}个字符
2. 不同排列但数值相同的视为同一种表示
3. 最终答案应为唯一的整数结果

请将最终答案放置在[answer]和[/answer]标签之间，例如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(n):
        if n == 1:
            return 4
        elif n <= 11:
            values = {1, 5, 10, 50}
            for _ in range(n-1):
                next_gen = set()
                for v in values:
                    next_gen.update([v+1, v+5, v+10, v+50])
                values = next_gen
            return len(values)
        else:
            return 49 * (n - 11) + 292
