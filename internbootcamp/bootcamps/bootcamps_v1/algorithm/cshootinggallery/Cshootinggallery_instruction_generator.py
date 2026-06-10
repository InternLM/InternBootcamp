import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random




class CshootinggalleryInstructionGenerator(BaseInstructionGenerator):
    """Cshootinggallery Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, coord_min=-10, coord_max=10, time_min=0, time_max=100):
        """
        初始化Cshootinggallery指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            coord_min: 参数描述
            coord_max: 参数描述
            time_min: 参数描述
            time_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.coord_min = coord_min
        self.coord_max = coord_max
        self.time_min = time_min
        self.time_max = time_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        generated_coords = set()
        targets = []
        
        # Generate targets with temporal continuity
        current_time = 0
        for _ in range(n):
            while True:
                x = random.randint(self.coord_min, self.coord_max)
                y = random.randint(self.coord_min, self.coord_max)
                if (x, y) not in generated_coords:
                    generated_coords.add((x, y))
                    break
            
            # Ensure temporal progression with possible overlaps
            ti = random.randint(current_time, max(current_time, self.time_max))
            current_time = ti  # Allow overlapping times for different coordinates
            pi = round(random.uniform(0, 1), 6)
            targets.append([x, y, ti, float(pi)])  # 使用列表保证序列化

        # Shuffle to test temporal ordering logic
        random.shuffle(targets)
        
        return {
            'n': len(targets),
            'targets': targets,
            'correct_answer': self._calculate_correct_answer(targets)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem = (
            "As King Copa's advisor, calculate the maximum expected hits in a shooting gallery with these rules:\n"
            "1. Targets appear at (x,y) coordinates at specific times\n"
            "2. Gun moves at 1 unit/sec from any starting point\n"
            "3. Hit probability is given for each target\n\n"
            f"Targets (n={question_case['n']}):\n"
        )
        problem += "\n".join([f"{x} {y} {t} {p:.6f}" for x, y, t, p in question_case['targets']])
        
        problem += (
            "\n\nProvide the maximum expected value with exactly 10 decimal places, enclosed in [answer] tags.\n"
            "Example: [answer]1.2345678901[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_correct_answer(targets):
        data = sorted(targets, key=lambda x: x[2])  # 按时间排序
        n = len(data)
        dp = [p[3] for p in data]

        for i in range(n):
            xi, yi, ti, _ = data[i]
            for j in range(i+1, n):
                xj, yj, tj, pj = data[j]
                distance = math.hypot(xj-xi, yj-yi)
                if distance <= (tj - ti):
                    dp[j] = max(dp[j], dp[i] + pj)
        return max(dp) if dp else 0.0
