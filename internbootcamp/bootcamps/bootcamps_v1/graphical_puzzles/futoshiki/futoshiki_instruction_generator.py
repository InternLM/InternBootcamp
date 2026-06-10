import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Dict
from typing import Any




class FutoshikiInstructionGenerator(BaseInstructionGenerator):
    """Futoshiki Bootcamp指令生成器"""
    
    def __init__(self, size=5, inequality_prob=0.3, retain_ratio=0.3):
        """
        初始化Futoshiki指令生成器
        
        Args:
            size: 参数描述
            inequality_prob: 参数描述
            retain_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.size = size
        self.inequality_prob = inequality_prob
        self.retain_ratio = retain_ratio
    
    def case_generator(self) -> dict:
        """生成带有唯一解的Futoshiki谜题实例"""
        solution = self._generate_latin_square()
        inequalities = self._generate_inequalities(solution)
        initial = self._generate_initial_grid(solution)
        return {
            'size': self.size,
            'initial': initial,
            'inequalities': inequalities
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        """生成面向用户的自然语言问题描述"""
        prompt = [
            "你是Futoshiki谜题专家，请根据以下条件解开谜题：",
            "\n规则说明：",
            "1. 填充1到N的整数（N为网格大小），满足：",
            "   - 每行和每列数字不重复",
            "   - 遵守所有不等式约束（>表示左边/上边数字更大）",
            f"\n初始网格（{case['size']}x{case['size']}，0表示空格）:"
        ]
        
        # 添加网格可视化
        for row in case['initial']:
            prompt.append("[" + " ".join(str(n) if n != 0 else "_" for n in row) + "]")
        
        # 添加不等式描述
        prompt.append("\n不等式约束：")
        for idx, ineq in enumerate(case['inequalities'], 1):
            c1, c2 = ineq['cell1'], ineq['cell2']
            direction = '右边' if c1[1]+1 == c2[1] else '下方'
            prompt.append(
                f"{idx}. 单元格({c1[0]}, {c1[1]}) {direction}的单元格应满足: "
                f"{ineq['symbol']}"
            )
        
        prompt.append(
            "\n将完整解答的二维数组放在[answer]标签内，例如：\n"
            "[answer]\n"
            "[[1,2,3],\n[2,3,1],\n[3,1,2]]\n"
            "[/answer]"
        )
        return "\n".join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_latin_square(self) -> List[List[int]]:
        """生成随机拉丁方阵作为解"""
        n = self.size
        base_row = list(range(1, n+1))
        random.shuffle(base_row)
        rows = [base_row[i:] + base_row[:i] for i in range(n)]
        random.shuffle(rows)
        perm = list(range(1, n+1))
        random.shuffle(perm)
        return [[perm[x-1] for x in row] for row in rows]

    def _generate_inequalities(self, solution: List[List[int]]) -> List[Dict]:
        """根据解生成不等式约束"""
        inequalities = []
        for i in range(self.size):
            for j in range(self.size):
                if j+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i][j+1]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i, j+1],
                        'symbol': '>' if a > b else '<'
                    })
                if i+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i+1][j]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i+1, j],
                        'symbol': '>' if a > b else '<'
                    })
        return inequalities

    def _generate_initial_grid(self, solution: List[List[int]]) -> List[List[int]]:
        """生成初始谜题网格"""
        n = self.size
        indices = [(i, j) for i in range(n) for j in range(n)]
        retain_num = int(len(indices) * self.retain_ratio)
        selected = random.sample(indices, retain_num)
        grid = [[0]*n for _ in range(n)]
        for i, j in selected:
            grid[i][j] = solution[i][j]
        return grid
