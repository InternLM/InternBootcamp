import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class KorlogicinductionparadoxInstructionGenerator(BaseInstructionGenerator):
    """Korlogicinductionparadox Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Korlogicinductionparadox指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.example_pool = [
            {
                "phenomenon": "实验室灯亮时老鼠逃跑",
                "hypotheses": ["灯光导致逃跑", "声音导致逃跑"],
                "contradiction": "灯光与声音开启条件互斥"
            },
            {
                "phenomenon": "火山喷发前动物躁动",
                "hypotheses": ["地震前兆假说", "气压变化假说"],
                "contradiction": "两种地质现象不会同时发生"
            }
        ]
        self.symbolic_templates = [
            "({q1} → {p}) ∧ ({q2} → {p}) ∧ ({q1} ⊻ {q2})",
            "{p} ⇒ ({h1} ∨ {h2}), 其中{h1}与{h2}矛盾"
        ]
    
    def case_generator(self):
        if random.random() < 0.5:
            return self._generate_example_case()
        else:
            return self._generate_symbolic_case()
    
    @staticmethod
    def prompt_func(question_case):
        if question_case["type"] == "example":
            desc = question_case
            return f'''观察到现象：{desc["phenomenon"]}
提出的两个互斥假设：
1. {desc["hypotheses"][0]}
2. {desc["hypotheses"][1]}
已知：{desc["contradiction"]}

这属于哪个逻辑悖论？
A. GB Paradox（矛盾假设归纳悖论）
B. BC Paradox（等价确认悖论）
C. LS Paradox（多重假设冲突悖论）
答案请用[[A/B/C]]格式给出'''
        else:
            return f'''请分析以下逻辑表达式对应的悖论类型：
{question_case["expression"]}

选项：
A. GB Paradox（具有矛盾假设的归纳悖论）
B. BC Paradox（基于等价转换的验证悖论） 
C. LS Paradox（多重合理假设的冲突悖论）
答案格式：[[答案字母]]''' 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_example_case(self):
        case = random.choice(self.example_pool)
        return {
            "type": "example",
            "phenomenon": case["phenomenon"],
            "hypotheses": case["hypotheses"],
            "contradiction": case["contradiction"],
            "correct_answer": "A"
        }

    def _generate_symbolic_case(self):
        template = random.choice(self.symbolic_templates)
        elements = {
            'p': random.choice(["现象X", "观测结果Y", "事件Z"]),
            'q1': random.choice(["假设α", "理论Q1", "推论A"]),
            'q2': random.choice(["假设β", "理论Q2", "推论B"]),
            'h1': random.choice(["H₁", "理论Γ"]),
            'h2': random.choice(["H₂", "理论Δ"])
        }
        return {
            "type": "symbolic",
            "expression": template.format(**elements),
            "correct_answer": "A"
        }
