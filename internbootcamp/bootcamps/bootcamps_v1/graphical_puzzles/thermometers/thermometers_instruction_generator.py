import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class ThermometersInstructionGenerator(BaseInstructionGenerator):
    """Thermometers Bootcamp指令生成器"""
    
    def __init__(self, size=5, num_thermometers=3, enforce_latin=True, max_retries=100):
        """
        初始化Thermometers指令生成器
        
        Args:
            size: 参数描述
            num_thermometers: 参数描述
            enforce_latin: 参数描述
            max_retries: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.size = size
        self.num_thermometers = num_thermometers
        self.enforce_latin = enforce_latin
        self.max_retries = max_retries
    
    def case_generator(self):
        if self.enforce_latin:
            solution = self._generate_latin_square(self.size)
        else:
            raise NotImplementedError("Non-Latin square puzzles are not supported yet.")

        thermometers = []
        for _ in range(self.num_thermometers):
            thermometer = None
            for _ in range(self.max_retries):
                start_row = random.randint(0, self.size-1)
                start_col = random.randint(0, self.size-1)
                path = self._generate_thermometer_path(solution, start_row, start_col)
                if path:
                    thermometer = {'bulb': path[0], 'path': path}
                    break
            if not thermometer:
                raise ValueError(f"Failed to generate thermometer after {self.max_retries} attempts")
            thermometers.append(thermometer)
        
        return {
            "size": self.size,
            "thermometers": thermometers,
            "enforce_latin": self.enforce_latin
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        def format_coord(coord):
            r, c = coord
            return f"行{r+1}列{c+1}"
        
        size = question_case['size']
        thermometers = question_case['thermometers']
        enforce_latin = question_case['enforce_latin']
        
        rules = [
            f"1. 在{size}x{size}的网格中填入1到{size}的数字。",
            "2. 每个温度计的路径必须从灯泡(●)开始严格递增。",
            f"3. 每{'行和列必须包含不重复的1到{size}' if enforce_latin else '行和列允许重复但需满足温度计约束'}。"
        ]
        
        thermo_desc = []
        for i, thermo in enumerate(thermometers, 1):
            path = thermo['path']
            bulb = format_coord(thermo['bulb'])
            tip = format_coord(path[-1])
            path_str = " → ".join(format_coord(p) for p in path)
            thermo_desc.append(f"温度计{i}: 从{bulb}到{tip}, 路径: {path_str}")

        return (
            "解决以下温度计谜题：\n\n" +
            "\n".join(rules) + "\n\n" +
            "温度计列表：\n" + "\n".join(thermo_desc) + "\n\n" +
            "将答案按行排列，每行数字用空格分隔，置于[answer]和[/answer]之间。示例：\n" +
            "[answer]\n1 2 3\n2 3 1\n3 1 2\n[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_latin_square(size):
        latin = []
        for i in range(size):
            row = [(i + j) % size + 1 for j in range(size)]
            latin.append(row)
        random.shuffle(latin)
        return latin

    @staticmethod
    def _generate_thermometer_path(solution, start_row, start_col):
        path = [(start_row, start_col)]
        current_value = solution[start_row][start_col]
        size = len(solution)

        while True:
            last_row, last_col = path[-1]
            neighbors = []
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = last_row + dr, last_col + dc
                if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in path:
                    next_value = solution[nr][nc]
                    if next_value > current_value:
                        neighbors.append((nr, nc, next_value))
            if not neighbors:
                break
            nr, nc, nv = random.choice(neighbors)
            path.append((nr, nc))
            current_value = nv

        return path if len(path) >= 2 else None
