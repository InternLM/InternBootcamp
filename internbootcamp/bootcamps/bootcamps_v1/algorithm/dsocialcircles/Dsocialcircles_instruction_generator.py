import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DsocialcirclesInstructionGenerator(BaseInstructionGenerator):
    """Dsocialcircles Bootcamp指令生成器"""
    
    def __init__(self, max_guests=10000, min_lr=0, max_lr=10**9):
        """
        初始化Dsocialcircles指令生成器
        
        Args:
            max_guests: 参数描述
            min_lr: 参数描述
            max_lr: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数优化说明:
            max_guests: 默认提升到10^4量级
            min_lr/max_lr: 严格遵循题目约束
        """
        self.max_guests = max_guests
        self.min_lr = min_lr
        self.max_lr = max_lr
    
    def case_generator(self):
        # 提高单人案例概率到30%
        if random.random() < 0.3:
            n = 1
        else:
            n = random.randint(1, self.max_guests)
        
        guests = []
        for _ in range(n):
            # 加强边界条件覆盖
            rand_type = random.random()
            if rand_type < 0.3:  # 完全对称型
                base = random.randint(self.min_lr, self.max_lr)
                l = r = base
            elif rand_type < 0.6:  # 单边极大
                l = random.choice([self.min_lr, self.max_lr])
                r = random.randint(self.min_lr, self.max_lr)
            else:  # 完全随机
                l = random.randint(self.min_lr, self.max_lr)
                r = random.randint(self.min_lr, self.max_lr)
            guests.append([l, r])
        return {"n": n, "guests": guests}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        guests = question_case["guests"]
        input_lines = [f"{n}"] + [f"{li} {ri}" for li, ri in guests]
        input_str = '\n'.join(input_lines)
        
        problem = (
            "## 晚宴椅子安排谜题\n"
            "需要为客人安排环形座位，每个客人要求：\n"
            "- 左侧至少有l_i把空椅子（朝向圆心方向）\n"
            "- 右侧至少有r_i把空椅子（朝向圆心方向）\n\n"
            "**关键规则**：\n"
            "1. 每个环形区域至少有1个客人\n"
            "2. 不同环形区域的椅子不共享\n"
            "3. 单独客人时：左右要求可以重叠\n"
            "   - 例：客人(5,6)需要7把椅子：max(5,6)+1=7\n\n"
            "**输入格式**：\n"
            f"- 第1行：n (1 ≤ n ≤ 1e5)\n"
            f"- 后接{n}行：每行两个整数l_i r_i\n\n"
            "**解答要求**：\n"
            "输出最小总椅子数，将答案放在[answer]标签内\n\n"
            "**当前题目**：\n"
            f"{input_str}\n"
            "[answer]在此填写答案[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

