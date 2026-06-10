from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cinnaanddima.Cinnaanddima_reward_calculator import CinnaanddimaRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any




class CinnaanddimaInteraction(BaseInteraction):
    """Cinnaanddima交互管理器"""
    
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
        score = CinnaanddimaRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cinnaanddima问题！"""
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
    @classmethod
    def _compute_correct_answer(cls, grid: list, n: int, m: int) -> str:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dp = [[0 for _ in range(m)] for __ in range(n)]
        visited = [[False for _ in range(m)] for __ in range(n)]
        in_cycle = [[False for _ in range(m)] for __ in range(n)]
        has_infinite = False

        def next_char(c: str) -> str:
            if c == 'D':
                return 'I'
            elif c == 'I':
                return 'M'
            elif c == 'M':
                return 'A'
            else:
                return 'D'

        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'D' and not visited[i][j]:
                    stack = [(i, j, 0, [])]
                    visited[i][j] = True
                    while stack:
                        x, y, steps, path = stack.pop()
                        if (x, y) in path:
                            has_infinite = True
                            break
                        new_path = path + [(x, y)]
                        current_char = grid[x][y]
                        next_c = next_char(current_char)
                        for dx, dy in directions:
                            nx = x + dx
                            ny = y + dy
                            if 0 <= nx < n and 0 <= ny < m:
                                if grid[nx][ny] == next_c and not visited[nx][ny]:
                                    visited[nx][ny] = True
                                    stack.append((nx, ny, steps + 1, new_path))
                        dp[x][y] = max(dp[x][y], steps // 4 + 1)
                    visited[i][j] = False
                    if has_infinite:
                        break
            if has_infinite:
                break

        if has_infinite:
            return "Poor Inna!"
        else:
            max_dima = 0
            for i in range(n):
                for j in range(m):
                    if dp[i][j] > max_dima:
                        max_dima = dp[i][j]
            if max_dima < 4:
                return "Poor Dima!"
            else:
                return str(max_dima // 4)
