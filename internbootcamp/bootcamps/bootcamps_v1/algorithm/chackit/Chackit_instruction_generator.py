import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def f(s):
    N = 0
    p = 0
    L = len(s)
    for i in range(len(s)):
        k = L - i - 1
        for j in range(int(s[i])):
            term1 = 9 * k * (10 ** k) // 2
            term2 = (p + j) * (10 ** k)
            N += term1 + term2
        p += int(s[i])
    return N

def g(N):
    if N == 0:
        return '0'
    s = ''
    L = 200  # 调整为200位
    for i in range(L):
        d = 0
        for j in range(10):
            test_s = s + str(j) + '0' * (L - i - 1)
            current_f = f(test_s)
            if current_f >= N:
                if j > 0:
                    s += str(j-1)
                else:
                    s += '0'  # 处理j=0的情况
                d = 1
                break
        if not d:
            s += '9'
    s = s.lstrip('0') or '0'
    return s

def find_test_case(a):
    s_list = []
    p_list = []
    i = 1
    while True:
        target = i * a
        m = g(target)
        q = f(m) % a
        for idx in range(len(p_list)):
            if q == p_list[idx] and int(m) > int(s_list[idx]):
                l = int(s_list[idx])
                r = int(m) - 1
                return (l, r)
        s_list.append(m)
        p_list.append(q)
        i += 1


class ChackitInstructionGenerator(BaseInstructionGenerator):
    """Chackit Bootcamp指令生成器"""
    
    def __init__(self, max_a=10**18):
        """
        初始化Chackit指令生成器
        
        Args:
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_a = max_a
    
    def case_generator(self):
        a = random.randint(1, self.max_a)
        l, r = find_test_case(a)
        # 确保数值有效性（示例代码逻辑保证）
        return {'a': a, 'l': l, 'r': r}
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        prompt = f"""Little X需要构造一个hack测试用例。请找到两个整数l和r，使得所有在区间[l, r]内数字的digit sum之和模{a}等于0。

输入要求：
- 第一行为整数a（此处a={a}）
- 输出l和r满足：1 ≤ l ≤ r < 10^200

关键规则：
1. digit sum定义：例如f(123)=1+2+3=6
2. 目标程序使用错误取模逻辑：ans = solve(l, r) % a; if (ans <=0) ans += a;
3. 你构造的(l, r)必须使正确结果为0，但目标程序会错误输出a

输出格式：
将答案放在[answer]标签内，例如：[answer]1 10[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

