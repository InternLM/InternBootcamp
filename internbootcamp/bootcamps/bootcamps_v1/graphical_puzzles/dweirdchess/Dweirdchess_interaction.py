from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dweirdchess.Dweirdchess_reward_calculator import DweirdchessRewardCalculator

# 导入依赖库
import re
import random




class DweirdchessInteraction(BaseInteraction):
    """Dweirdchess交互管理器"""
    
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
        score = DweirdchessRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dweirdchess问题！"""
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
    def _generate_move_vectors(self, n):
        if self.current_move_type == 'rook':
            vectors = []
            for dx in range(-n+1, n):
                if dx != 0:
                    vectors.append((dx, 0))
            for dy in range(-n+1, n):
                if dy != 0:
                    vectors.append((0, dy))
            return list(set(vectors))
        elif self.current_move_type == 'knight':
            return [ (dx, dy) for dx in (-2, -1, 1, 2) for dy in (-2, -1, 1, 2) if abs(dx) + abs(dy) == 3 ]
        else:
            vectors = []
            for _ in range(random.randint(3, 6)):
                dx = random.randint(-n+1, n-1)
                dy = random.randint(-n+1, n-1)
                if dx == 0 and dy == 0:
                    continue
                vectors.append((dx, dy))
            return list(set(vectors))

    def _generate_o_positions(self, n):
        count = random.randint(self.min_o, self.max_o)
        positions = set()
        while len(positions) < count:
            x = random.randint(0, n-1)
            y = random.randint(0, n-1)
            positions.add((x, y))
        return list(positions)

    def _generate_grid(self, n, o_positions, move_vectors):
        grid = [['.' for _ in range(n)] for _ in range(n)]
        o_coords = set((x, y) for x, y in o_positions)

        for x, y in o_coords:
            grid[y][x] = 'o'

        for x, y in o_coords:
            for dx, dy in move_vectors:
                tx = x + dx
                ty = y + dy
                if 0 <= tx < n and 0 <= ty < n:
                    if (tx, ty) not in o_coords:
                        grid[ty][tx] = 'x'

        return grid
