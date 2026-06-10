import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccycleinmaze.Ccycleinmaze_reward_calculator import CcycleinmazeRewardCalculator

# 导入依赖库
from collections import deque
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcycleinmazeVerificationTool(BaseTool):
    """Ccycleinmaze验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = CcycleinmazeRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"CcycleinmazeVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
