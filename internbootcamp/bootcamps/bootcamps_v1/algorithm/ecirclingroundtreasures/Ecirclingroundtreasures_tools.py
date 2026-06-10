import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ecirclingroundtreasures.Ecirclingroundtreasures_reward_calculator import EcirclingroundtreasuresRewardCalculator

# 导入依赖库
import random
import re
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EcirclingroundtreasuresVerificationTool(BaseTool):
    """Ecirclingroundtreasures验证工具"""
    
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
            score = EcirclingroundtreasuresRewardCalculator.verify_score(
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
            logger.error(f"EcirclingroundtreasuresVerificationTool执行错误: {str(e)}")
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
    def compute_max_profit(identity):
        n, m = identity['n'], identity['m']
        grid = identity['grid']
        treasure_values = identity['treasure_values']
        sx = sy = None
        treasures = []
        bombs = []
        for i in range(n):
            for j in range(m):
                c = grid[i][j]
                if c == 'S':
                    sx, sy = i+1, j+1
                elif c.isdigit():
                    treasures.append((int(c), i+1, j+1))
                elif c == 'B':
                    bombs.append((i+1, j+1))
        treasures.sort()
        gx, gy, val = [], [], []
        for num, x, y in treasures:
            gx.append(x)
            gy.append(y)
            val.append(treasure_values[num-1])
        for x, y in bombs:
            gx.append(x)
            gy.append(y)
            val.append(-10000)
        m_objects = len(gx)
        tot = 1 << m_objects
        w = [0] * tot
        for mask in range(tot):
            total = 0
            for j in range(m_objects):
                if mask & (1 << j):
                    total += val[j]
            w[mask] = total
        INF = float('inf')
        dp = [[[INF]*tot for _ in range(m+2)] for __ in range(n+2)]
        dp[sx][sy][0] = 0
        q = deque([(sx, sy, 0)])
        max_profit = -INF
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        while q:
            x, y, mask = q.popleft()
            if x == sx and y == sy:
                current_profit = w[mask] - dp[x][y][mask]
                max_profit = max(max_profit, current_profit)
            for i in range(4):
                tx, ty = x + dx[i], y + dy[i]
                if tx < 1 or tx > n or ty < 1 or ty > m:
                    continue
                cell = grid[tx-1][ty-1]
                if cell not in ('.', 'S'):
                    continue
                new_mask = mask
                for j in range(m_objects):
                    nx, ny = x, y
                    obj_x, obj_y = gx[j], gy[j]
                    if nx == obj_x and ny < obj_y:
                        if tx < obj_x:
                            new_mask ^= (1 << j)
                    elif tx == obj_x and ty < obj_y:
                        if nx < obj_x:
                            new_mask ^= (1 << j)
                if dp[tx][ty][new_mask] > dp[x][y][mask] + 1:
                    dp[tx][ty][new_mask] = dp[x][y][mask] + 1
                    q.append((tx, ty, new_mask))
        return max(max_profit, 0)
