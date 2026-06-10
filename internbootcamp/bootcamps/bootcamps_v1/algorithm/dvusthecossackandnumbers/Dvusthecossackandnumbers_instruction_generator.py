import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
import re




class DvusthecossackandnumbersInstructionGenerator(BaseInstructionGenerator):
    """Dvusthecossackandnumbers Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, max_int=5, **params):
        """
        初始化Dvusthecossackandnumbers指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            max_int: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.n_min = max(n_min, 1)
        self.n_max = n_max
        self.max_int = max_int  # 控制生成的整数范围
    
    def case_generator(self):
        """生成满足以下条件的案例：
        1. Σa_i = 0（精确到5位小数）
        2. 所有a_i的小数部分随机分布
        3. 包含至少一个整数a_i（当n>=2时）
        """
        while True:
            n = random.randint(self.n_min, self.n_max)
            if n == 1:
                return {'n': 1, 'a_list': [0.00000]}  # 特例处理
            
            # 生成基础整数集合，确保总和为0
            b = []
            sum_b = 0
            for _ in range(n-1):
                num = random.randint(-self.max_int, self.max_int)
                if num == 0:  # 避免生成过多0
                    num = random.choice([-1, 1])
                b.append(num)
                sum_b += num
            # 添加最后一个数使总和为0
            last_num = -sum_b
            if last_num == 0 and n > 1:  # 避免两个0相邻
                last_num = random.choice([-1, 1])
            b.append(last_num)
            
            # 加入至少一个整数（当n>=2时）
            int_pos = random.randint(0, n-1)
            b[int_pos] = b[int_pos]

            # 生成小数部分
            decimal_parts = []
            positive_deltas = []
            negative_deltas = []
            for num in b:
                if num == 0:
                    decimal = 0.0  # 强制整数
                elif random.random() < 0.2:  # 20%概率生成整数
                    decimal = 0.0
                else:
                    decimal = round(random.uniform(0.00001, 0.99999), 5)
                
                if num > 0:
                    positive_deltas.append(decimal)
                elif num < 0:
                    negative_deltas.append(-decimal)
                decimal_parts.append(decimal)

            # 调整小数部分总和为整数
            total_diff = sum(positive_deltas) + sum(negative_deltas)
            adjust = round(total_diff, 0) - total_diff
            if adjust != 0:
                if positive_deltas:
                    adj_index = random.choice(range(len(positive_deltas)))
                    positive_deltas[adj_index] = round(positive_deltas[adj_index] + adjust, 5)
                elif negative_deltas:
                    adj_index = random.choice(range(len(negative_deltas)))
                    negative_deltas[adj_index] = round(negative_deltas[adj_index] + adjust, 5)

            # 构建最终的a_i列表
            a_list = []
            pos_idx = 0
            neg_idx = 0
            for num in b:
                if num > 0:
                    delta = positive_deltas[pos_idx]
                    pos_idx += 1
                    a = num + delta
                elif num < 0:
                    delta = negative_deltas[neg_idx]
                    neg_idx += 1
                    a = num + delta
                else:
                    a = 0.0
                a_rounded = round(a, 5)
                a_list.append(a_rounded)

            # 最终验证
            if abs(sum(a_list)) < 1e-8:
                return {'n': n, 'a_list': a_list}
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        prompt = (
            "Vus the Cossack需要将以下实数四舍五入为整数，使得总和保持为0。\n"
            "规则：\n"
            "1. 每个数b_i必须是a_i的地板值(floor)或天花板值(ceil)\n"
            "2. 最终Σb_i必须等于0\n"
            "3. |a_i - b_i| < 1 必须成立\n"
            f"输入：\n{case['n']}\n" +
            "\n".join(f"{a:.5f}" for a in case['a_list']) + 
            "\n输出：每行一个整数，包含在[answer]标签内\n"
            "示例:\n[answer]\n3\n-1\n-2\n0\n[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

