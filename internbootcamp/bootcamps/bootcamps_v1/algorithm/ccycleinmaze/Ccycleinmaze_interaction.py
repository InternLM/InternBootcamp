from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccycleinmaze.Ccycleinmaze_reward_calculator import CcycleinmazeRewardCalculator

# 导入依赖库
from collections import deque
import random
import re




class CcycleinmazeInteraction(BaseInteraction):
    """Ccycleinmaze交互管理器"""
    
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
        score = CcycleinmazeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccycleinmaze问题！"""
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
    @staticmethod
    def _generate_solution(n, m, k, grid):
        """ 使用BFS生成正确答案 """
        if k % 2 != 0:
            return "IMPOSSIBLE"

        # 查找起始点
        start_x, start_y = -1, -1
        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'X':
                    start_x, start_y = i, j
                    break
            if start_x != -1:
                break

        dx = [1, 0, 0, -1]  # D, L, R, U
        dy = [0, -1, 1, 0]
        dirs = ['D', 'L', 'R', 'U']
        size = n * m
        dist = [float('inf')] * size
        q = deque([(start_x, start_y, 0)])
        dist[start_x * m + start_y] = 0

        # BFS计算最短路径
        while q:
            x, y, d = q.popleft()
            for i in range(4):
                nx, ny = x + dx[i], y + dy[i]
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] != '*':
                    pos = nx * m + ny
                    if dist[pos] > d + 1:
                        dist[pos] = d + 1
                        q.append((nx, ny, d + 1))

        path = []
        x, y = start_x, start_y
        for step in range(k):
            found = False
            for i in range(4):  # 按字典序选择方向
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] != '*':
                    pos = nx * m + ny
                    remaining = k - step - 1
                    if dist[pos] <= remaining:
                        path.append(dirs[i])
                        x, y = nx, ny
                        found = True
                        break
            if not found:
                return "IMPOSSIBLE"

        # 最终必须回到起点
        return ''.join(path) if (x, y) == (start_x, start_y) else "IMPOSSIBLE"
