import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import List




class CereaderdisplayInstructionGenerator(BaseInstructionGenerator):
    """Cereaderdisplay Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Cereaderdisplay指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = n  # 确保n的范围符合题目要求
        if not 1 <= n <= 2000:
            raise ValueError("n must be between 1 and 2000")
    
    def case_generator(self):
        """逆向生成有效案例：先生成命令模式再推导目标图像"""
        n = self.n
        # 生成随机命令集合（保证可逆性）
        commands = self.generate_valid_commands(n)
        # 生成目标网格
        grid = self.simulate_commands(n, commands)
        return {
            'n': n,
            'grid': [''.join(map(str, row)) for row in grid],
            'correct_answer': len(commands)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        grid = "\n".join(question_case['grid'])
        return f"""您需要为新型电子阅读器计算最小操作命令数。显示屏规格：{n}x{n}，初始全白。目标图案：
{grid}

每条命令(x,y)会翻转：
1. 第x行从第min(x,y)列到第max(x,y)列
2. 第y列从第min(x,y)行到第max(x,y)行

请给出所需的最小命令数量，并置于[answer][/answer]标签内。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_commands(self, n: int) -> List[tuple]:
        """基于参考算法逻辑生成最小命令集合"""
        # 根据题目参考算法逆向生成命令
        commands = []
        # 随机选择对角线操作概率
        if random.random() < 0.3:
            diag_count = random.randint(0, n)
            commands += [(i+1, i+1) for i in random.sample(range(n), diag_count)]

        # 随机生成非对角线操作
        non_diag = [(i+1, j+1) for i in range(n) for j in range(n) if i != j]
        commands += random.sample(non_diag, k=random.randint(0, len(non_diag)))
        return list(set(commands))  # 去重后返回

    def simulate_commands(self, n: int, commands: List[tuple]) -> List[List[int]]:
        """精确模拟命令作用效果"""
        grid = [[0]*n for _ in range(n)]
        for x, y in commands:
            # 处理行x的区域
            start_col = min(x, y) - 1
            end_col = max(x, y) - 1
            for col in range(start_col, end_col + 1):
                if 0 <= col < n:
                    grid[x-1][col] ^= 1

            # 处理列y的区域
            start_row = min(x, y) - 1
            end_row = max(x, y) - 1
            for row in range(start_row, end_row + 1):
                if 0 <= row < n:
                    grid[row][y-1] ^= 1
        return grid

    @staticmethod
    def calculate_min_commands(n: int, grid: List[List[int]]) -> int:
        """完整实现参考算法"""
        a = [[0]*(n+2) for _ in range(n+2)]
        b = [[0]*(n+2) for _ in range(n+2)]
        A = [[0]*(n+2) for _ in range(n+2)]
        B = [[0]*(n+2) for _ in range(n+2)]
        ans = 0

        # 处理右上三角区域
        for J in range(n, 1, -1):
            i, j = 1, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (a[i][j] + b[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    a[i][j-1] = a[i][j] + 1
                    b[i+1][j] = b[i][j] + 1
                else:
                    a[i][j-1] = a[i][j]
                    b[i+1][j] = b[i][j]
                i += 1
                j += 1

        # 处理左下三角区域
        for J in range(2, n+1):
            i, j = n, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (A[i][j] + B[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    A[i][j+1] = A[i][j] + 1
                    B[i-1][j] = B[i][j] + 1
                else:
                    A[i][j+1] = A[i][j]
                    B[i-1][j] = B[i][j]
                i -= 1
                j -= 1

        # 处理对角线元素
        for i in range(1, n+1):
            current_value = grid[i-1][i-1]
            total = (a[i][i] + b[i][i] + A[i][i] + B[i][i]) % 2
            if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                ans += 1

        return ans
