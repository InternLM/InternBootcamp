import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EwizardsandnumbersInstructionGenerator(BaseInstructionGenerator):
    """Ewizardsandnumbers Bootcamp指令生成器"""
    
    def __init__(self, max_value=10**18, prob_zero=0.1):
        """
        初始化Ewizardsandnumbers指令生成器
        
        Args:
            max_value: 参数描述
            prob_zero: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_value = max_value
        self.prob_zero = prob_zero
    
    def case_generator(self):
        """生成覆盖全部可能性的测试用例"""
        a = self._generate_number()
        b = self._generate_number()
        # 确保生成边界情况
        if random.random() < 0.2:
            a, b = sorted((a, b))
        return {'a': a, 'b': b}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        b = question_case['b']
        return f"""在魔法师的数字博弈游戏中，黑板上有两个数字a和b。两个玩家轮流进行操作：
        
1. 减法咒语：将较大数减去除以较小数的任意正整数倍（结果非负）
2. 模数咒语：将较大数对较小数取模

当任一数字为0时游戏结束，无法行动的玩家失败。给定a={a}, b={b}，判断先手玩家是否必胜？

答案请严格使用[answer]First[/answer]或[answer]Second[/answer]格式，大小写敏感。示例：[answer]Second[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_number(self):
        if random.random() < self.prob_zero:
            return 0
        return random.randint(0, self.max_value)

    @staticmethod
    def win(a, b):
        """优化后的迭代实现版博弈判断"""
        memo = {}
        stack = [(a, b)]

        while stack:
            a, b = stack.pop()
            if a > b:
                a, b = b, a
            key = (a, b)

            if key in memo:
                continue

            if a == 0:
                memo[key] = False
                continue

            mod = b % a
            mod_key = (mod, a) if mod <= a else (a, mod)

            if mod_key not in memo:
                stack.append(key)
                stack.append(mod_key)
            else:
                if not memo[mod_key]:
                    memo[key] = True
                else:
                    quotient = b // a
                    memo[key] = (quotient % (a + 1)) % 2 == 0
        return memo.get((a, b), False)
