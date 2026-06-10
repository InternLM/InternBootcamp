import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BandreyandproblemInstructionGenerator(BaseInstructionGenerator):
    """Bandreyandproblem Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100):
        """
        初始化Bandreyandproblem指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        probs = [round(random.uniform(0, 1), 6) for _ in range(n)]
        
        sorted_probs = sorted(probs, reverse=True)
        optimal = 0.0
        none_fail = 1.0
        for p in sorted_probs:
            candidate = none_fail * p + (1 - p) * optimal
            if candidate > optimal:
                optimal = candidate
                none_fail *= (1 - p)
        
        return {
            "n": n,
            "probabilities": probs,
            "expected": optimal
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        probs_str = ' '.join(f"{p:.6f}" for p in question_case["probabilities"])
        return f"""你是安德烈，需要选择一组朋友来最大化恰好得到一个问题的概率。请根据输入数据计算最大概率。

规则：
1. 选择任意数量的朋友，每个被选中的朋友独立以给定概率成功
2. 只有当恰好一个朋友成功时，安德烈不会生气
3. 需要选择最优的朋友组合使成功概率最大

输入格式：
第一行为整数n（朋友数量）
第二行是n个实数（保留6位小数）

示例输入1：
4
0.1 0.2 0.3 0.8

示例输出1：
0.800000000000

示例输入2：
2
0.1 0.2

示例输出2：
0.260000000000

当前问题：
输入：
{question_case['n']}
{probs_str}

请输出最大概率（必须包含至少9位小数），并将最终答案放在[answer]和[/answer]之间。例如：[answer]0.260000000000[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

