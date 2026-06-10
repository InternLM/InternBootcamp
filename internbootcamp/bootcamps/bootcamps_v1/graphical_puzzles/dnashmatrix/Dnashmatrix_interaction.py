from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dnashmatrix.Dnashmatrix_reward_calculator import DnashmatrixRewardCalculator

# 导入依赖库
import re
import random




class DnashmatrixInteraction(BaseInteraction):
    """Dnashmatrix交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = DnashmatrixRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dnashmatrix问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法
    def generate_valid_case(self):
        """生成有效案例并标记is_valid=True"""
        grid = self.generate_valid_grid()
        valid_cells = self.simulate_grid(grid)
        return {
            "n": self.n,
            "cells": valid_cells,
            "is_valid": True
        }

    def generate_invalid_case(self):
        """生成无效案例并标记is_valid=False"""
        n = self.n
        # 创建一个必定矛盾的案例：所有单元格要求最终到达同一个X但路径冲突
        valid_grid = self.generate_valid_grid()
        cells = self.simulate_grid(valid_grid)
        # 随机选择一个单元格，强制其终止点为另一个单元格，但该单元格并非X且路径无法到达
        i, j = random.randint(0, n-1), random.randint(0, n-1)
        target = (random.randint(1, n), random.randint(1, n))
        while target == (i+1, j+1) or valid_grid[i][j] == 'X':
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            target = (random.randint(1, n), random.randint(1, n))
        cells[i][j] = target
        return {
            "n": n,
            "cells": cells,
            "is_valid": False  # 强制标记为无效
        }

    def generate_valid_grid(self):
        """生成合法网格，确保指令不会导致越界"""
        grid = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                possible = []
                if i > 0:
                    possible.append('U')
                if i < self.n - 1:
                    possible.append('D')
                if j > 0:
                    possible.append('L')
                if j < self.n - 1:
                    possible.append('R')
                possible.append('X')
                # 优先设置X的概率
                if random.random() < self.x_prob:
                    char = 'X'
                else:
                    char = random.choice(possible)
                row.append(char)
            grid.append(row)
        return grid

    def simulate_grid(self, grid):
        """计算每个单元格的终止点"""
        cells = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                termination = self.simulate_cell(i, j, grid)
                row.append(termination)
            cells.append(row)
        return cells

    def simulate_cell(self, r, c, grid):
        """模拟玩家移动，返回终止点或(-1,-1)"""
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1

    @classmethod
    def check_valid_solution(cls, solution_lines, identity):
        """验证有效案例的网格正确性"""
        n = identity["n"]
        if len(solution_lines) != n + 1:
            return False
        grid = solution_lines[1:]
        # 格式检查
        for row in grid:
            if len(row) != n or any(c not in "UDLRX" for c in row):
                return False
        # 指令合法性检查
        for i in range(n):
            for j in range(n):
                c = grid[i][j]
                if (c == 'U' and i == 0) or (c == 'D' and i == n-1) or \
                   (c == 'L' and j == 0) or (c == 'R' and j == n-1):
                    return False
        # 终止点一致性检查
        for i in range(n):
            for j in range(n):
                simulated = cls.static_simulate_cell(i, j, grid)
                expected = identity["cells"][i][j]
                if simulated != expected:
                    return False
        return True

    @staticmethod
    def static_simulate_cell(r, c, grid):
        """静态方法：模拟单元格移动"""
        n = len(grid)
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1
