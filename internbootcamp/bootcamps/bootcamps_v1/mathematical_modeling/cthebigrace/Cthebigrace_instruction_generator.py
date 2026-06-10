import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import gcd

# === 源文件中的全局函数 ===

def compute_probability(t, w, b):
    """优化边界条件处理和极值计算逻辑"""
    if t == 0:
        return (0, 1)
    
    # 计算最大公约数和最小公倍数
    gcd_val = gcd(w, b)
    lcm = (w * b) // gcd_val
    
    # 处理超大数值的溢出保护
    try:
        full_cycles = t // lcm
        remaining = t % lcm
    except:
        return (0, 1)
    
    min_step = min(w, b)
    count = (full_cycles + 1) * min_step - 1
    
    # 调整剩余部分
    if remaining < min_step - 1:
        count -= (min_step - 1 - remaining)
    
    # 结果规范化
    count = max(0, count)  # 确保非负
    total_gcd = gcd(count, t)
    
    return (count // total_gcd, t // total_gcd)


class CthebigraceInstructionGenerator(BaseInstructionGenerator):
    """Cthebigrace Bootcamp指令生成器"""
    
    def __init__(self, max_t=10**18, max_step=10**18):
        """
        初始化Cthebigrace指令生成器
        
        Args:
            max_t: 参数描述
            max_step: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数范围支持题目要求的 1 ≤ t, w, b ≤ 5e18
        增加边界案例生成概率：
        - 50% 生成普通随机案例
        - 30% 生成互质步长案例
        - 20% 生成极值案例
        """
        self.max_t = max_t
        self.max_step = max_step
    
    def case_generator(self):
        """智能生成多类型测试案例"""
        case_type = random.choices(
            ['random', 'coprime', 'extreme'],
            weights=[0.5, 0.3, 0.2],
            k=1
        )[0]
        
        if case_type == 'coprime':
            # 生成互质步长
            w = random.randint(1, self.max_step)
            while True:
                b = random.randint(1, self.max_step)
                if gcd(w, b) == 1:
                    break
            t = random.randint(1, self.max_t)
        
        elif case_type == 'extreme':
            # 极值案例：最大参数或最小参数
            params = [
                (self.max_t, self.max_step, self.max_step),
                (1, 1, 1),
                (self.max_t, 1, self.max_step),
                (random.randint(1, 100), 1, 1)
            ]
            t, w, b = random.choice(params)
        
        else:  # random
            t = random.randint(1, self.max_t)
            w = random.randint(1, self.max_step)
            b = random.randint(1, self.max_step)
        
        return {'t': t, 'w': w, 'b': b}
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        rule_desc = (
            "关键规则说明：\n"
            "1. Willman的最大行程：找到最大整数k使得k×w ≤ L\n"
            "2. Bolt的最大行程：找到最大整数m使得m×b ≤ L\n"
            "3. 平局条件：k×w = m×b\n"
            "4. 概率计算：满足条件的L数量 / 总可能性数t"
        )
        return f"""## 赛跑平局概率问题

比赛参数：
- 跑道最大长度 (t)：{case['t']}
- Willman步长 (w)：{case['w']}
- Bolt步长 (b)：{case['b']}

{rule_desc}

请计算平局概率，并以最简分数[answer]分子/分母[/answer]格式回答。例如：[answer]3/7[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

