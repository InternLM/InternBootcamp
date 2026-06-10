import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ddistinctpaths.Ddistinctpaths_reward_calculator import DdistinctpathsRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DdistinctpathsVerificationTool(BaseTool):
    """Ddistinctpaths验证工具"""
    
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
            score = DdistinctpathsRewardCalculator.verify_score(
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
            logger.error(f"DdistinctpathsVerificationTool执行错误: {str(e)}")
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
    def generate_valid_full_grid(self, n, m, k):
        grid = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                used = set()
                if i > 0:
                    used.add(grid[i-1][j])
                if j > 0:
                    used.add(grid[i][j-1])
                available = [c for c in range(1, k+1) if c not in used]
                if not available:
                    return None
                grid[i][j] = min(available)
        return grid

    @staticmethod
    def compute_solution(n, m, k, grid):
        if n + m > 11 or (n + m - 1) > k:
            return 0
        grid = [[cell-1 if cell !=0 else -1 for cell in row] for row in grid]
        a = [[-1]*(m+2) for _ in range(n+2)]
        for i in range(n):
            for j in range(m):
                a[i+1][j+1] = grid[i][j] if grid[i][j] != -1 else -1
        lim2 = [[0]*(m+2) for _ in range(n+2)]
        s = 0
        for i in range(1, n+1):
            for j in range(1, m+1):
                if a[i][j] != -1:
                    s |= 1 << a[i][j]
                    if i < n:
                        lim2[i][j] |= 1 << a[i][j]
                    if j < m:
                        lim2[i][j] |= 1 << a[i][j]
        for i in range(n, 0, -1):
            for j in range(m, 0, -1):
                lim2[i][j] |= lim2[i+1][j] | lim2[i][j+1]
                if a[i][j] != -1 and (lim2[i][j] & (1 << a[i][j])):
                    return 0
        v = []
        for color in range(k):
            if not (s & (1 << color)):
                v.append(color)
        if not v:
            return 1
        # DFS to compute answer
        memo = {}
        def dfs(x, y, cnt, lim):
            if x > n:
                return 1
            if y > m:
                return dfs(x+1, 1, cnt, lim)
            key = (x, y, cnt, tuple(map(tuple, lim)))
            if key in memo:
                return memo[key]
            current_lim = lim[x-1][y] | lim[x][y-1]
            total = 0
            for color in range(k):
                if a[x][y] != -1 and color != a[x][y]:
                    continue
                if current_lim & (1 << color):
                    continue
                if lim2[x][y] & (1 << color):
                    continue
                if not (s & (1 << color)):
                    if a[x][y] == -1 and (cnt >= len(v) or color > v[cnt]):
                        continue
                new_lim = [row[:] for row in lim]
                new_lim[x][y] = current_lim | (1 << color)
                new_cnt = cnt
                if a[x][y] == -1 and not (s & (1 << color)):
                    if color == v[cnt]:
                        new_cnt = min(len(v)-1, cnt + 1)
                res = dfs(x, y+1, new_cnt, new_lim)
                if a[x][y] == -1 and color in v and cnt < len(v) and color == v[cnt]:
                    total = (total + res * (len(v) - cnt)) % MOD
                else:
                    total = (total + res) % MOD
            memo[key] = total
            return total
        lim_init = [[0]*(m+2) for _ in range(n+2)]
        result = dfs(1, 1, 0, lim_init)
        return result
