import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DskillsInstructionGenerator(BaseInstructionGenerator):
    """Dskills Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dskills指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'n_min': 3,
            'n_max': 10,
            'A_min': 50,
            'A_max': 500,
            'cf_min': 1,
            'cf_max': 1000,
            'cm_min': 1,
            'cm_max': 1000,
            'm_min': 0,
            'm_max': 10**18
        }
        self.params.update(params)
    
    def case_generator(self):
        params = self.params
        n = random.randint(params['n_min'], params['n_max'])
        A = random.randint(params['A_min'], params['A_max'])
        cf = random.randint(params['cf_min'], params['cf_max'])
        cm = random.randint(params['cm_min'], params['cm_max'])
        m = random.randint(params['m_min'], params['m_max'])
        
        a_initial = [
            random.randint(0, A-1) if random.random() < 0.8 else A
            for _ in range(n)
        ]
        return {
            'n': n,
            'A': A,
            'cf': cf,
            'cm': cm,
            'm': m,
            'a_initial': a_initial
        }
    
    @staticmethod
    def prompt_func(question_case):  # 此处原先缺少正确缩进
        n = question_case['n']
        A = question_case['A']
        cf = question_case['cf']
        cm = question_case['cm']
        m = question_case['m']
        a_str = ' '.join(map(str, question_case['a_initial']))
        prompt = (
            f"你是游戏Hacknet中的一名角色，需要帮助Lesha分配他的技能点以获得最大的战力值（Force）。\n"
            f"你的角色当前有{n}项技能，每项的当前等级为：{a_str}。每项技能的最高等级为{A}。\n"
            f"Lesha拥有{m}个货币单位，每个单位可以提升任一技能1级（不能超过最高等级A）。\n"
            f"战力值的计算方式为：\n"
            f"- 完美技能的数量（即等于最高等级A的技能数）乘以系数{cf}。\n"
            f"- 所有技能中最低等级的技能等级乘以系数{cm}。\n"
            f"请分配货币，使得战力值最大。\n"
            f"输出格式要求：\n"
            f"第一行输出最大战力值，第二行输出各技能的最终等级，用空格分隔。\n"
            f"请将答案放在[answer]标签内，例如：\n"
            f"[answer]\n最大值\n最终等级列表...\n[/answer]"
        )
        return prompt  # 补全函数体并确保缩进 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_force(n, A, cf, cm, m, a_initial):
        sorted_a = sorted(a_initial)
        total = sum(sorted_a)

        # 处理全满的特殊情况
        if total + m >= n * A:
            return cf * n + cm * A, [A]*n

        # 计算可能的最大完美技能数
        perfect = 0
        for i in reversed(range(n)):
            cost = A - sorted_a[i]
            if m >= cost:
                perfect += 1
                m -= cost
            else:
                break

        # 提高最低技能
        min_level = sorted_a[0]
        for i in range(1, n-perfect):
            delta = sorted_a[i] - sorted_a[i-1]
            if m >= delta * i:
                min_level += delta
                m -= delta * i
            else:
                min_level += m // i
                m %= i
                break

        final_force = perfect * cf + min_level * cm
        final_levels = [max(a, min_level) for a in a_initial]
        # 升满完美技能
        for i in reversed(range(n)):
            if final_levels[i] < A and perfect > 0:
                final_levels[i] = A
                perfect -= 1
        return final_force, final_levels
