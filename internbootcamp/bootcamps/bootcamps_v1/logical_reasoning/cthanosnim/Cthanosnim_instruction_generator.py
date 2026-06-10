import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CthanosnimInstructionGenerator(BaseInstructionGenerator):
    """Cthanosnim Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=50, **params):
        """
        初始化Cthanosnim指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_n = max(2, min_n)
        self.max_n = min(50, max_n)
        possible_n = [n for n in range(self.min_n, self.max_n + 1) if n % 2 == 0]
        if not possible_n:
            raise ValueError("No valid even n in the given range")
        self.possible_n = possible_n
    
    def case_generator(self):
        n = random.choice(self.possible_n)
        mid_index = n // 2
        
        # Ensure max(left) +1 <=50 for Alice case
        if random.random() < 0.5:
            # Generate Bob case (sorted[0] == sorted[mid_index])
            base = random.randint(1, 50)
            piles = [base] * (mid_index + 1) + [random.randint(base, 50) for _ in range(n - mid_index - 1)]
        else:
            # Generate Alice case with safe value range
            max_left = random.randint(1, 49)
            left = [random.randint(1, max_left) for _ in range(mid_index)]
            right = [random.randint(max_left + 1, 50) for _ in range(n - mid_index)]
            piles = left + right
        
        random.shuffle(piles)
        return {
            'n': n,
            'piles': piles
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        piles = question_case['piles']
        return f"""Alice和Bob正在玩一个石子堆游戏，规则如下：

- 游戏使用{n}个石子堆（保证是偶数）
- 两人轮流操作，Alice先手
- 每次必须选择恰好{n//2}个非空堆，并从每个选中堆移除至少1个石子
- 无法进行合法操作（当剩余非空堆少于{n//2}时）的玩家判负

当前游戏参数：
n = {n}
各堆石子数 = {', '.join(map(str, piles))}

请分析游戏结果并判断胜者。将最终答案放在[answer]标签内，例如：[answer]Alice[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

