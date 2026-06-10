import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dsolvethemaze.Dsolvethemaze_reward_calculator import DsolvethemazeRewardCalculator

# 导入依赖库
import random
from collections import deque

# === 源文件中的全局函数 ===

def get_adj(x, y, n_rows, m_cols):
    return [(nx, ny) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] 
            if 0<=(nx:=x+dx)<m_cols and 0<=(ny:=y+dy)<n_rows]

def solve_maze(n, m, original_grid):
    grid = [row.copy() for row in original_grid]
    good = set()
    bad = []
    
    # 收集所有好人坏人位置
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 'G':
                good.add((y,x))
            elif grid[y][x] == 'B':
                bad.append((y,x))
    
    # 处理坏人周围的墙
    valid = True
    for y, x in bad:
        # 检查坏人是否离出口太近（曼哈顿距离）
        if (n-1 - y) + (m-1 - x) <= 1:
            valid = False
        
        # 将坏人周围的空地变为墙
        for ax, ay in get_adj(x, y, n, m):
            if grid[ay][ax] == '.':
                grid[ay][ax] = '#'
        
        if not valid: break
    
    # 提前终止条件
    if not valid:
        return "Yes" if len(good) == 0 else "No"
    
    # 出口被墙阻挡的情况
    if grid[n-1][m-1] == '#':
        return "Yes" if len(good) == 0 else "No"
    
    # BFS检查可达性
    marked = [[False]*m for _ in range(n)]
    queue = deque([(n-1, m-1)])
    marked[n-1][m-1] = True
    valid = True
    
    while queue:
        y, x = queue.popleft()
        
        # 遇到坏人直接失败
        if grid[y][x] == 'B':
            valid = False
            break
        
        # 处理相邻单元格
        for ax, ay in get_adj(x, y, n, m):
            if not marked[ay][ax] and grid[ay][ax] != '#':
                marked[ay][ax] = True
                queue.append((ay, ax))
                if (ay, ax) in good:
                    good.remove((ay, ax))
    
    return "Yes" if valid and not good else "No"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DsolvethemazeVerificationTool(BaseTool):
    """Dsolvethemaze验证工具"""
    
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
            score = DsolvethemazeRewardCalculator.verify_score(
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
            logger.error(f"DsolvethemazeVerificationTool执行错误: {str(e)}")
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

