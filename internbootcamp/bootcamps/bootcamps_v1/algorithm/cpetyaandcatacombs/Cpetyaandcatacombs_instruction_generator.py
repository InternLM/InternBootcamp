import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpetyaandcatacombsInstructionGenerator(BaseInstructionGenerator):
    """Cpetyaandcatacombs Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20):
        """
        初始化Cpetyaandcatacombs指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_n < 1:
            raise ValueError("min_n must be at least 1")
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """增强测试案例生成逻辑，保证生成有效冲突场景"""
        n = random.randint(self.min_n, self.max_n)
        t = []
        conflict_pool = []
        
        # 强制生成至少一个重复的ti值（当n≥2时）
        for j in range(n):
            i = j + 1
            # 前两个元素特殊处理保证至少一个冲突
            if j == 0:
                ti = 0  # 第一个ti只能是0
            elif j == 1 and n >= 2:
                ti = 0  # 强制第二个ti为0触发冲突
            else:
                # 40%概率复用已有值，60%随机生成
                if conflict_pool and random.random() < 0.4:
                    ti = random.choice(conflict_pool)
                else:
                    ti = random.randint(0, i-1)
            
            conflict_pool.append(ti)
            t.append(ti)
        return {"n": n, "t": t}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        t_str = ' '.join(map(str, question_case['t']))
        prompt = f"""你是探险家Vasya，正在分析Petya的日志本以确定巴黎地下墓穴中可能的最小房间数量。根据以下规则进行分析：

Petya在时间0时位于某个房间，之后每过一分钟移动到另一个房间。每次进入一个房间时：
1. 如果该房间之前被访问过，他会记录上一次访问该房间的时间（即ti等于上一次的时间）；
2. 如果这是第一次访问该房间，他会在日志中记录一个严格小于当前时间i的非负整数。

现在给出Petya的日志记录，请确定满足这些记录所需的最小可能房间数量。

输入格式：
- 第一行是一个整数n（表示日志记录的数量）
- 第二行包含n个非负整数t1 t2 ... tn（0 ≤ ti < i）

例如，输入样例：
2
0 0
对应的输出是2，因为至少需要两个房间。

当前问题输入：
{n}
{t_str}

请仔细分析问题，并给出正确的答案。将你的最终答案放置在[answer]和[/answer]的标签之间，例如：[answer]2[/answer]。确保答案是一个整数。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

