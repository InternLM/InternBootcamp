import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CgivenlengthandsumofdigitsInstructionGenerator(BaseInstructionGenerator):
    """Cgivenlengthandsumofdigits Bootcamp指令生成器"""
    
    def __init__(self, max_m=100, max_s=900):
        """
        初始化Cgivenlengthandsumofdigits指令生成器
        
        Args:
            max_m: 参数描述
            max_s: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_m = max_m
        self.max_s = max_s
    
    def case_generator(self):
        """生成具有统计学意义的测试案例，确保30%的有效案例覆盖边界条件"""
        if random.random() < 0.3:
            m = random.randint(1, self.max_m)
            if m == 1:
                s = random.choice([0] + list(range(1, 10)))  # 包含零的特殊情况
            else:
                s = random.randint(1, m*9)
        else:
            m = random.randint(1, self.max_m)
            s = random.randint(0, self.max_s)
        return {'m': m, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        """结构化提示模板确保格式一致性"""
        m, s = question_case['m'], question_case['s']
        return f"""找到满足以下条件的{m}位数字：
━┅━━┅━ 核心规则 ━┅━━┅━
1. 数字总位数 = {m}位
2. 所有数字之和 = {s}
3. 禁止前导零（除非是唯一的零）

┏━━━━━ 输出要求 ━━━━━┓
将最小数和最大数按格式[answer]min max[/answer]输出
无效案例使用[answer]-1 -1[/answer]

例如：
[answer]69 96[/answer] 或 [answer]-1 -1[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _has_valid_solution(cls, m, s):
        """解存在性判断逻辑"""
        if m == 1:
            return 0 <= s <= 9
        return 1 <= s <= m*9

    @classmethod
    def compute_solutions(cls, m, s):
        """双指针法生成极值"""
        def gen_min():
            if m == 1: return str(s)
            res = [0]*m
            remaining = s
            for i in reversed(range(1, m)):
                val = min(9, remaining-1)
                res[i] = val
                remaining -= val
            res[0] = remaining
            return ''.join(map(str, res)) if res[0] <=9 else None

        def gen_max():
            res = []
            remaining = s
            for _ in range(m):
                val = min(9, remaining)
                res.append(str(val))
                remaining -= val
            return ''.join(res) if remaining ==0 else None

        if not cls._has_valid_solution(m, s):
            return ("-1 -1", True)
        return (f"{gen_min()} {gen_max()}", False) if gen_min() and gen_max() else ("-1 -1", True)
