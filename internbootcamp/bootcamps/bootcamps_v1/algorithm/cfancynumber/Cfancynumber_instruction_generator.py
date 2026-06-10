import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_beautiful_number(n, k, original_number):
    s = list(original_number)
    c = [0] * 10
    for i in range(n):
        digit = int(s[i])
        c[digit] += 1

    def choosevalue(m):
        nonlocal c, n, k, s
        if c[m] >= k:
            return (0, original_number)
        p = s.copy()
        total_cost = 0
        remain = k - c[m]
        for i in range(1, 10):
            R = m + i
            L = m - i
            # Process R direction (higher digits)
            if R <= 9 and remain > 0:
                for j in range(n):
                    if remain <= 0:
                        break
                    if int(p[j]) == R:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            # Process L direction (lower digits)
            if L >= 0 and remain > 0:
                for j in range(n-1, -1, -1):
                    if remain <= 0:
                        break
                    if int(p[j]) == L:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            if remain <= 0:
                break
        new_number = ''.join(p)
        return (total_cost, new_number)

    best_cost = float('inf')
    best_number = None
    for m in range(10):
        current_cost, current_number = choosevalue(m)
        if current_cost < best_cost:
            best_cost = current_cost
            best_number = current_number
        elif current_cost == best_cost:
            if current_number < best_number:
                best_number = current_number
    return (best_cost, best_number)


class CfancynumberInstructionGenerator(BaseInstructionGenerator):
    """Cfancynumber Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, fixed_n=None, fixed_k=None):
        """
        初始化Cfancynumber指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            fixed_n: 参数描述
            fixed_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.fixed_n = fixed_n
        self.fixed_k = fixed_k
    
    def case_generator(self):
        if self.fixed_n is not None:
            n = self.fixed_n
        else:
            n = random.randint(self.min_n, self.max_n)
        
        if self.fixed_k is not None:
            k = self.fixed_k
        else:
            k = random.randint(2, n)
        
        original_number = ''.join(random.choices('0123456789', k=n))
        return {
            'n': n,
            'k': k,
            'original_number': original_number
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        original = question_case['original_number']
        prompt = f"""你是一位车牌号码优化师。请帮助Vasya将他的车牌号码转换为美丽号，使得转换的总花费最小，并且在多个解中选择字典序最小的。具体规则如下：

- 车牌号码由{n}位数字组成。
- 美丽号要求至少有{k}个相同的数字。
- 每次更改一个数字的花费是原数字和新数字的绝对差。
- 总花费是所有更改的花费之和。
- 如果有多个总花费相同的最优解，必须选择字典序最小的那个。

当前的问题实例是：

输入：
{n} {k}
{original}

请输出两行，第一行是最小的总花费，第二行是新的号码。将你的最终答案放置在[answer]和[/answer]标签之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

