from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.tents.tents_reward_calculator import TentsRewardCalculator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Tuple




class TentsInteraction(BaseInteraction):
    """Tents交互管理器"""
    
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
        score = TentsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个tents问题！"""
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
    def _generate_tent_positions(self) -> List[Tuple[int, int]]:
        available = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        tents = []
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        random.shuffle(positions)

        for x, y in positions:
            if available[x][y]:
                tents.append((x, y))
                # Mark surrounding cells as unavailable
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            available[nx][ny] = False
        return tents

    def _place_trees(self, tent_positions) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        tree_positions = []

        for x, y in tent_positions:
            directions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            random.shuffle(directions)
            placed = False
            for dx, dy in directions:
                if 0 <= dx < self.rows and 0 <= dy < self.cols:
                    if grid[dx][dy] == 0 and (dx, dy) not in tent_positions:
                        grid[dx][dy] = 1
                        tree_positions.append((dx, dy))
                        placed = True
                        break
            if not placed:
                return None, None
        return grid, tree_positions

    def _validate_tree_tents(self, grid, tents, trees) -> bool:
        # Check tent adjacency
        for i in range(len(tents)):
            for j in range(i+1, len(tents)):
                x1, y1 = tents[i]
                x2, y2 = tents[j]
                if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                    return False

        # Check tree-tent mapping
        tree_counts = {(i,j):0 for i in range(self.rows) for j in range(self.cols) if grid[i][j]}
        for x, y in tents:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if grid[nx][ny]:
                        tree_counts[(nx, ny)] += 1
        return all(c == 1 for c in tree_counts.values())
