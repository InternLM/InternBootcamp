import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cgardenofthesun.Cgardenofthesun_reward_calculator import CgardenofthesunRewardCalculator

# 导入依赖库
import random
from collections import deque
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CgardenofthesunVerificationTool(BaseTool):
    """Cgardenofthesun验证工具"""
    
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
            score = CgardenofthesunRewardCalculator.verify_score(
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
            logger.error(f"CgardenofthesunVerificationTool执行错误: {str(e)}")
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
    def generate_tree(self, n, m):
        """使用Prim算法生成生成树结构"""
        grid = [[False for _ in range(m)] for _ in range(n)]
        directions = [(-1,0), (0,1), (1,0), (0,-1)]

        # 随机选择起点
        start = (random.randint(0, n-1), random.randint(0, m-1))
        grid[start[0]][start[1]] = True
        frontier = []

        # 初始化边界
        for dx, dy in directions:
            nx, ny = start[0]+dx, start[1]+dy
            if 0 <= nx < n and 0 <= ny < m:
                frontier.append((nx, ny))

        while frontier:
            # 随机选择边界点
            idx = random.randint(0, len(frontier)-1)
            x, y = frontier.pop(idx)

            # 寻找相邻的已选节点
            neighbors = []
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny]:
                    neighbors.append((nx, ny))

            if neighbors:
                # 随机选择一个邻居连接
                parent = random.choice(neighbors)
                grid[x][y] = True

                # 添加新边界
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < n and 0 <= ny < m and not grid[nx][ny]:
                        if (nx, ny) not in frontier:
                            frontier.append((nx, ny))

        return grid

    def create_valid_initial_x(self, solution):
        """生成满足条件的初始X集合"""
        n, m = len(solution), len(solution[0])
        candidates = [(i,j) for i in range(n) for j in range(m) if solution[i][j]]
        initial = set()
        banned = set()

        # 随机打乱候选顺序
        random.shuffle(candidates)

        for x, y in candidates:
            # 检查8邻域是否冲突
            conflict = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x+dx, y+dy) in initial:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                initial.add((x, y))
                # 将周围8格标记为禁止区
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        banned.add((x+dx, y+dy))

        return initial

    def create_initial_grid(self, n, m, initial_x):
        grid = [['.' for _ in range(m)] for _ in range(n)]
        for x, y in initial_x:
            grid[x][y] = 'X'
        return [''.join(row) for row in grid]
