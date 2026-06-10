import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CvanyaandexamsInstructionGenerator(BaseInstructionGenerator):
    """Cvanyaandexams Bootcamp指令生成器"""
    
    def __init__(self, max_exams=10, max_r=1000, max_bi=10**6):
        """
        初始化Cvanyaandexams指令生成器
        
        Args:
            max_exams: 参数描述
            max_r: 参数描述
            max_bi: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_exams = max_exams
        self.max_r = max_r
        self.max_bi = max_bi
    
    def case_generator(self):
        # 生成基础参数（确保avg <= r）
        n = random.randint(1, self.max_exams)
        r = random.randint(1, self.max_r)
        avg = random.randint(1, min(r, 10**6))  # 正确约束avg范围

        # 生成考试数据（存在初始分数可能达标的情况）
        exams = []
        for _ in range(n):
            ai = random.randint(1, r)
            bi = random.randint(1, self.max_bi)
            exams.append([ai, bi])

        return {
            'n': n,
            'r': r,
            'avg': avg,
            'exams': exams
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        exams_desc = "\n".join(
            [f"- 第{i+1}门考试：当前分数 {ai} 分（最高可至{r}分），每提升1分需要 {bi} 篇小作文"
             for i, (ai, (r, bi)) in enumerate(zip(
                 [e[0] for e in question_case['exams']],
                 [(question_case['r'], e[1]) for e in question_case['exams']]
             ))]
        )
        
        return f"""Vanya希望通过提高考试分数来获得奖学金。当前情况：
- 已参加考试科目：{question_case['n']}门
- 每科最高分数限制：{question_case['r']}分
- 目标平均分：{question_case['avg']}分

各科详情：
{exams_desc}

请计算Vanya需要撰写的最小作文数量。答案格式为单独一个整数，置于[answer]标签内，如：[answer]1234[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

