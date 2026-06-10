import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve_min_repaint(n, k, s_str):
    if n == 0:
        return 0, ""
    
    s = list(s_str)
    if k > 2:
        modified = False
        for i in range(1, n):
            if s[i] == s[i-1]:
                available = set(string.ascii_uppercase[:k]) - {s[i-1]}
                if i < n-1:
                    available.discard(s[i+1])
                s[i] = sorted(available)[0]
                modified = True
        
        if modified and s[0] == s[1]:
            available = set(string.ascii_uppercase[:k]) - {s[1]}
            if n >= 3:
                available.discard(s[2])
            s[0] = sorted(available)[0]
        
        cnt = sum(1 for a, b in zip(s, s_str) if a != b)
        return cnt, ''.join(s)
    else:
        pattern1 = ['A' if i%2 ==0 else 'B' for i in range(n)]
        pattern2 = ['B' if i%2 ==0 else 'A' for i in range(n)]
        cnt1 = sum(c != sc for c, sc in zip(pattern1, s))
        cnt2 = sum(c != sc for c, sc in zip(pattern2, s))
        if cnt1 <= cnt2:
            return cnt1, ''.join(pattern1)
        return cnt2, ''.join(pattern2)


class CcolorstripeInstructionGenerator(BaseInstructionGenerator):
    """Ccolorstripe Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, k_min=2, k_max=4):
        """
        初始化Ccolorstripe指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 1)
        self.n_max = n_max
        self.k_min = max(k_min, 2)
        self.k_max = min(k_max, 26)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k = random.randint(self.k_min, self.k_max)
        
        # 生成具有非连续重复的初始字符串
        colors = string.ascii_uppercase[:k]
        if n == 1:
            original_s = random.choice(colors)
        else:
            original_s = [random.choice(colors)]
            for _ in range(1, n):
                # 保证至少有一个可能的重复
                if len(original_s) < 2 or random.random() < 0.4:
                    original_s.append(original_s[-1])
                else:
                    original_s.append(random.choice([c for c in colors if c != original_s[-1]]))
            original_s = ''.join(original_s)
        
        # 确保问题有解
        min_repaints, correct_s = solve_min_repaint(n, k, original_s)
        return {
            'n': n,
            'k': k,
            'original_s': original_s,
            'min_repaints': min_repaints,
            'correct_s': correct_s
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        original_s = question_case['original_s']
        color_desc = "、".join(string.ascii_uppercase[:k])
        return f"""作为颜色优化专家，请将{n}个单元格的颜色条纹（{original_s}）重新涂色，要求：
⒈ 相邻颜色不能相同
⒉ 只能使用{color_desc}这{k}种颜色
⒊ 修改次数最少

请按以下格式输出答案：
[answer]
修改次数
最终颜色序列
[/answer]

示例（k=3时）：
输入：6 3 ABBACC
回答：
[answer]
2
ABCACA
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

