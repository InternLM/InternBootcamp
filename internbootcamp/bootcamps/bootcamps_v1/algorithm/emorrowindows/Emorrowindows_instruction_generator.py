import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EmorrowindowsInstructionGenerator(BaseInstructionGenerator):
    """Emorrowindows Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Emorrowindows指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = params.get('n', 0)
        self.x = params.get('x', 2)
        self.a = params.get('a', [])
    
    def case_generator(self):
        n = random.randint(0, 105)
        x = random.randint(2, 10**9)
        a = [random.randint(1, 10**9) for _ in range(n)]
        return {'n': n, 'x': x, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        x = question_case['x']
        a = question_case['a']
        a_str = ', '.join(map(str, a))
        prompt = (
            f"Vasya在游戏中的库存物品数量介于2和{x}之间。他有{n}种模式，每种模式的ai值分别是：{a_str}。每种模式会显示页面总数bi。"
            f"请确定Vasya需要查看多少种模式才能唯一确定物品数量。如果无法确定，请输出-1。"
            f"你的答案应放在[answer]标签中，例如：[answer]2[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_correct_answer(n, x, a):
        a_set = set(a)
        if 1 in a_set and x > 2:
            return 1
        if x <= 2:
            return 1
        # 使用筛法计算质数，但限制在x不超过1e6，以避免内存问题
        max_sieve_x = min(x, 10**6)
        sieve = [True] * (max_sieve_x + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(max_sieve_x**0.5) + 1):
            if sieve[i]:
                sieve[i*i : max_sieve_x+1 : i] = [False] * len(sieve[i*i : max_sieve_x+1 : i])
        primes = [i for i, is_prime in enumerate(sieve) if is_prime]
        # 检查所有质数是否都在a_set中
        for p in primes:
            if p > x:
                break
            if p not in a_set:
                return -1
        return len(primes)
