import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CplayingwithsuperglueInstructionGenerator(BaseInstructionGenerator):
    """Cplayingwithsuperglue Bootcamp指令生成器"""
    
    def __init__(self, n_range=(1, 100), m_range=(1, 100)):
        """
        初始化Cplayingwithsuperglue指令生成器
        
        Args:
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数增强校验逻辑，确保合法棋盘范围
        """
        self.n_min = max(1, n_range[0])
        self.n_max = max(1, n_range[1])
        self.m_min = max(1, m_range[0])
        self.m_max = max(1, m_range[1])
        assert self.n_min <= self.n_max and self.m_min <= self.m_max, "Invalid grid size range"
    
    def case_generator(self):
        """
        完全随机生成合法案例，时间复杂度优化为O(1)
        """
        while True:
            n = random.randint(self.n_min, self.n_max)
            m = random.randint(self.m_min, self.m_max)
            if n * m >= 2:  # 严格满足题目约束
                break
        
        # 生成第一组坐标
        x1, y1 = random.randint(1, n), random.randint(1, m)
        
        # 高效生成第二组不重复坐标
        while True:
            x2, y2 = random.randint(1, n), random.randint(1, m)
            if (x1, y1) != (x2, y2):
                break
        
        return {
            'n': n, 'm': m,
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2
        }
    
    @staticmethod
    def prompt_func(question_case):
        """
        增强规则描述的完整性，包含所有必要细节
        """
        rule_desc = [
            "1. Players alternate turns, starting with First",
            "2. First moves one unglued chip (L/R/U/D), can enter glued square (immobilizes chip)",
            "3. Second places glue on an empty square each turn",
            "4. First wins if chips meet after any move",
            "5. Second wins if both chips are immobilized without meeting"
        ]
        return f"""Analyze this chip movement game (Board: {question_case['n']}x{question_case['m']}, Chips at ({question_case['x1']},{question_case['y1']}) & ({question_case['x2']},{question_case['y2']})).

Rules:
{chr(10).join(rule_desc)}

Determine the winner with optimal play. Answer strictly as [answer]First[/answer] or [answer]Second[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

