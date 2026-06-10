import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.daliceandthedoll.Daliceandthedoll_reward_calculator import DaliceandthedollRewardCalculator

# 导入依赖库
import random
import bisect

# === 源文件中的全局函数 ===

def solve(n, m, obstacles):
    if n == 0 or m == 0:
        return "No"
    
    obstacles_x = [[-1, m] for _ in range(n)]
    obstacles_y = [[-1, n] for _ in range(m)]
    
    for x, y in obstacles:
        x0 = x - 1
        y0 = y - 1
        bisect.insort(obstacles_x[x0], y0)
        bisect.insort(obstacles_y[y0], x0)

    for row in obstacles_x:
        row.sort()
    for col in obstacles_y:
        col.sort()

    flag = 1
    traversed = 0
    turn = 1
    curr_x, curr_y = 0, -1
    lower_x, upper_x = 0, n
    lower_y, upper_y = -1, m

    while flag == 1:
        flag = 0
        if turn == 1:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y)
            next_y = min(upper_y-1, obstacles_x[curr_x][idx]-1)
            if next_y > curr_y:
                traversed += next_y - curr_y
                flag = 1
                turn = 2
                curr_y, upper_y = next_y, next_y
        elif turn == 2:
            idx = bisect.bisect_right(obstacles_y[curr_y], curr_x)
            next_x = min(upper_x-1, obstacles_y[curr_y][idx]-1)
            if next_x > curr_x:
                traversed += next_x - curr_x
                flag = 1
                turn = 3
                curr_x, upper_x = next_x, next_x
        elif turn == 3:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y) - 1
            next_y = max(lower_y+1, obstacles_x[curr_x][idx]+1)
            if next_y < curr_y:
                traversed += curr_y - next_y
                flag = 1
                turn = 4
                curr_y, lower_y = next_y, next_y
        else:
            idx = bisect.bisect_left(obstacles_y[curr_y], curr_x) - 1
            next_x = max(lower_x+1, obstacles_y[curr_y][idx]+1)
            if next_x < curr_x:
                traversed += curr_x - next_x
                flag = 1
                turn = 1
                curr_x, lower_x = next_x, next_x

    total_cells = n * m - len(obstacles)
    return "Yes" if traversed == total_cells else "No"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DaliceandthedollVerificationTool(BaseTool):
    """Daliceandthedoll验证工具"""
    
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
            score = DaliceandthedollRewardCalculator.verify_score(
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
            logger.error(f"DaliceandthedollVerificationTool执行错误: {str(e)}")
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

