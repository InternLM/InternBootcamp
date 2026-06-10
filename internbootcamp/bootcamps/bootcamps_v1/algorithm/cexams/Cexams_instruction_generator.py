import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CexamsInstructionGenerator(BaseInstructionGenerator):
    """Cexams Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5000, max_a=10**9):
        """
        初始化Cexams指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数调整支持边界条件
        :param min_n: 考试数下限 (1 ≤ n ≤ 5000)
        :param max_n: 考试数上限 (约束至5000)
        :param max_a: ai最大值 (支持题目要求的1e9)
        """
        self.min_n = max(1, min_n)
        self.max_n = min(5000, max_n)
        self.max_a = max_a
    
    def case_generator(self):
        """生成保证数据有效性的测试案例"""
        n = random.randint(self.min_n, self.max_n)
        exams = []
        
        # 生成有效数据的主逻辑
        for _ in range(n):
            # 生成合法ai（≥2）和bi（1 ≤ bi < ai）
            a = random.randint(2, self.max_a)
            b = random.randint(1, a-1)
            exams.append((a, b))
        
        # 添加30%概率的边界案例
        if random.random() < 0.3:
            # 生成全逆序案例（排序时会自动校正）
            exams.sort(reverse=True)
        else:
            # 随机打乱数据顺序
            random.shuffle(exams)
        
        return {
            "n": n,
            "exams": exams
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """优化格式描述的准确性"""
        exams = question_case['exams']
        n = question_case['n']
        
        problem = (
            "你需要在满足时间顺序约束的条件下，找到完成所有考试的最早最后一天。\n\n"
            "**规则说明**\n"
            "1. 每个考试有两个可选日期：官方日期a_i和提前日期b_i（b_i < a_i）\n"
            "2. 必须按照官方日期的非递减顺序参加考试\n"
            "3. 实际参加日期可以任选b_i或a_i\n"
            "4. 要求找到完成所有考试的最早可能最后一天\n\n"
            "**输入格式**\n"
            f"第一行：{n}\n" +
            "\n".join(f"{a} {b}" for a, b in exams) +
            "\n\n**答案要求**\n将最终答案放在[answer]标签内，例如：[answer]5[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

